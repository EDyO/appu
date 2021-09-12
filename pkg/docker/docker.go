package docker

import (
	"context"
	"io"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/mount"
	"github.com/docker/docker/client"
)

// RunAppuContainer runs the `image` Docker image with the defined `volumes` mounted as specified.
// The argument `volumes` maps local files to container paths, replacing any existing match.
func RunAppuContainer(image string, volumes map[string]string) (io.ReadCloser, error) {
	cli, err := getDockerClient()
	if err != nil {
		return nil, err
	}

	out, err := run(cli, image, volumes)
	if err != nil {
		return nil, err
	}

	return out, err
}

func getDockerClient() (*client.Client, error) {
	return client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
}

func run(cli *client.Client, image string, volumes map[string]string) (io.ReadCloser, error) {
	ctx := context.Background()

	mounts := []mount.Mount{}
	for source, target := range volumes {
		mounts = append(mounts, mount.Mount{
			Type:   mount.TypeBind,
			Source: source,
			Target: target,
		})
	}

	resp, err := cli.ContainerCreate(ctx, &container.Config{
		Image: image,
		Tty:   false,
	},
		&container.HostConfig{
			Mounts: mounts,
		}, nil, nil, "")
	if err != nil {
		return nil, err
	}

	if err := cli.ContainerStart(ctx, resp.ID, types.ContainerStartOptions{}); err != nil {
		return nil, err
	}

	statusCh, errCh := cli.ContainerWait(ctx, resp.ID, container.WaitConditionNotRunning)
	select {
	case err := <-errCh:
		if err != nil {
			return nil, err
		}
	case <-statusCh:
	}

	return cli.ContainerLogs(ctx, resp.ID, types.ContainerLogsOptions{ShowStdout: true})
}
