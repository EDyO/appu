package appu

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/antchfx/htmlquery"
	"github.com/antchfx/xpath"
	"github.com/ifosch/stationery/pkg/gdrive"
	"github.com/ifosch/stationery/pkg/stationery"
	"golang.org/x/net/html"
	"google.golang.org/api/drive/v3"
	"gopkg.in/yaml.v2"
)

// GetPubDate returns the `time.Time` value for current publication.
var GetPubDate = time.Now

// GetFeed returns the content of the XML feed defined in `URL`, or an
// error.
var GetFeed = func(URL string) (string, error) {
	resp, err := http.Get(URL)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(bodyBytes), nil
}

var errNoMatchingScripts = fmt.Errorf(
	"no matching scripts, please add a query returning one %s",
	"single document",
)

var tooManyResults = func(r []*drive.File) error {
	return fmt.Errorf(
		"query returns too many documents (%v), %s",
		len(r),
		" expecting only one",
	)
}

// GetScript returns the content of the script which name matches the
// `episodeTag` in HTML, or an error.
var GetScript = func(episodeTag string) (string, error) {
	q := fmt.Sprintf("name contains '%v'", episodeTag)

	svc, err := gdrive.GetService(
		os.Getenv("DRIVE_CREDENTIALS_FILE"),
	)
	if err != nil {
		return "", err
	}

	if len(q) == 0 {
		return "", errNoMatchingScripts
	}

	r, err := stationery.GetFiles(svc, q)
	if err != nil {
		return "", err
	}

	if len(r) > 1 {
		return "", tooManyResults(r)
	}

	content, err := stationery.ExportHTML(svc, r[0])
	if err != nil {
		return "", err
	}

	return content, nil
}

// ScriptFieldHook represents hooks to catch fields from the script.
type ScriptFieldHook struct {
	Name      string `yaml:"name"`
	Hook      string `yaml:"hook"`
	List      bool   `yaml:"list"`
	Attribute string `yaml:"attribute"`
}

// Podcast contains all the parameters to get the episode details for
// a podcast.
type Podcast struct {
	FeedURL          string `yaml:"feedURL"`
	MasterURLPattern string `yaml:"masterURLPattern"`
	PublishURL       string `yaml:"publishURL"`
	DistributionID   string `yaml:"distributionID"`
	DirectFields     struct {
		Cover         string `yaml:"cover"`
		Artist        string `yaml:"artist"`
		Album         string `yaml:"album"`
		IntroURL      string `yaml:"introURL"`
		EpisodeBucket string `yaml:"episodeBucket"`
	} `yaml:"directFields"`
	ScriptFieldHooks   []ScriptFieldHook `yaml:"scriptFieldHooks"`
	EpisodeScriptHooks map[string]string `yaml:"episodeScriptHooks"`
	trackName          string
	scriptTree         *html.Node
	feedTree           *html.Node
	details            map[string]interface{}
}

// NewPodcast constructs the `Podcast` object for a `trackName`
// according with the properties defined in the `YAMLFile`, or an
// error.
func NewPodcast(trackName, YAMLFile string) (*Podcast, error) {
	f, err := os.ReadFile(YAMLFile)
	if err != nil {
		return nil, err
	}

	podcast := &Podcast{
		trackName: trackName,
		details:   map[string]interface{}{},
	}
	err = yaml.Unmarshal([]byte(f), podcast)
	if err != nil {
		return nil, err
	}

	err = podcast.downloadScript()
	if err != nil {
		return nil, err
	}

	err = podcast.downloadFeed()
	if err != nil {
		return nil, err
	}

	err = podcast.extractProperties()
	if err != nil {
		return nil, err
	}

	return podcast, nil
}

func (p *Podcast) episodeScriptHook() string {
	numberRE := regexp.MustCompile("[0-9]+")

	tag := ""
	for k, v := range p.EpisodeScriptHooks {
		if strings.Contains(p.trackName, k) {
			tag = v
		}
	}
	if tag == "" {
		tag = p.EpisodeScriptHooks["default"]
	}

	return fmt.Sprintf(
		"%s %s",
		tag,
		numberRE.FindString(p.trackName),
	)
}

func (p *Podcast) downloadScript() error {
	script, err := GetScript(p.episodeScriptHook())
	if err != nil {
		return err
	}

	p.scriptTree, err = htmlquery.Parse(
		strings.NewReader(script),
	)
	if err != nil {
		return err
	}

	return nil
}

func (p *Podcast) downloadFeed() error {
	feed, err := GetFeed(p.FeedURL)
	if err != nil {
		return err
	}

	p.feedTree, err = htmlquery.Parse(
		strings.NewReader(feed),
	)
	if err != nil {
		return err
	}

	return nil
}

func (p *Podcast) trackNo() (int, error) {
	expr, err := xpath.Compile("count(//item)")
	if err != nil {
		return 0, err
	}

	trackNo := int(expr.Evaluate(
		htmlquery.CreateXPathNavigator(p.feedTree),
	).(float64)) + 1

	return trackNo, nil
}

func (p *Podcast) extractPropertiesFromScript() {
	for _, hook := range p.ScriptFieldHooks {
		if hook.List {
			htmlNodes := htmlquery.Find(
				p.scriptTree,
				hook.Hook,
			)
			contents := []string{}
			for _, htmlNode := range htmlNodes {
				contents = append(
					contents,
					htmlquery.InnerText(
						htmlNode,
					),
				)
			}
			p.details[hook.Name] = contents
		} else {
			htmlNode := htmlquery.FindOne(
				p.scriptTree,
				hook.Hook,
			)
			p.details[hook.Name] = getSingleHookDetails(
				hook,
				htmlNode,
			)
		}
	}
}

func getSingleHookDetails(
	hook ScriptFieldHook,
	htmlNode *html.Node,
) interface{} {
	if hook.Attribute != "" {
		return htmlquery.SelectAttr(
			htmlNode,
			hook.Attribute,
		)
	}
	return htmlquery.InnerText(htmlNode)
}

func (p *Podcast) extractPropertiesFromFeed() error {
	trackNo, err := p.trackNo()
	if err != nil {
		return err
	}

	p.details["trackNo"] = trackNo
	return nil
}

func (p *Podcast) extractDirectProperties() {
	p.details["cover"] = p.DirectFields.Cover
	p.details["artist"] = p.DirectFields.Artist
	p.details["album"] = p.DirectFields.Album
	p.details["intro"] = p.DirectFields.IntroURL
	p.details["bucket"] = p.DirectFields.EpisodeBucket
}

func (p *Podcast) extractProperties() (err error) {
	p.extractPropertiesFromScript()
	p.extractDirectProperties()
	p.details["pubDate"] = GetPubDate()
	p.details["master"] = strings.Replace(
		p.MasterURLPattern,
		"<FILE>",
		p.trackName,
		1,
	)
	p.details["episodeURL"] = fmt.Sprintf(
		"%s/%s",
		p.PublishURL,
		strings.Replace(
			p.trackName,
			".master",
			"",
			1,
		),
	)
	p.details["distributionID"] = p.DistributionID
	err = p.extractPropertiesFromFeed()

	return err
}
