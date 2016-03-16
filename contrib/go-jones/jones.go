package jones

import (
	"encoding/json"
	"fmt"
	"github.com/samuel/go-zookeeper/zk"
	"os"
	"sync"
	"time"
)

type watcher struct {
	conn *zk.Conn
	path string
	cb   func([]byte)
	stop chan struct{}
}

func (w *watcher) watch() {
	for {
		data, _, events, err := w.conn.GetW(w.path)
		if err != nil {
			continue
		}
		w.cb(data)
		select {
		case <-events:
		case <-w.stop:
			return
		}
	}
}

func (w *watcher) close() {
	w.stop <- struct{}{}
}

type JonesClient struct {
	conn           *zk.Conn
	hostname       string
	nodemapWatcher *watcher
	configWatcher  *watcher
	service        string
	nodemap        map[string]string
	config         map[string]interface{}
	synced         bool
	wg             sync.WaitGroup
}

func (client *JonesClient) DialAndSync(servers []string) error {
	err := client.Dial(servers)
	if err != nil {
		return err
	}

	client.wg.Wait()
	return nil
}

func (client *JonesClient) Dial(servers []string) error {
	var err error
	client.conn, _, err = zk.Connect(servers, time.Second)
	if err != nil {
		return err
	}

	client.wg.Add(1)

	client.nodemapWatcher = &watcher{
		conn: client.conn,
		path: fmt.Sprintf("/services/%s/nodemaps", client.service),
		cb:   client.nodemapChanged,
	}
	go client.nodemapWatcher.watch()
	return nil
}

func (client *JonesClient) nodemapChanged(data []byte) {
	if len(data) > 0 {
		json.Unmarshal(data, &client.nodemap)
	}
	conf, ok := client.nodemap[client.hostname]
	if !ok {
		conf = fmt.Sprintf("/services/%s/conf", client.service)
	}

	if client.configWatcher != nil {
		client.configWatcher.close()
	}

	client.configWatcher = &watcher{
		conn: client.conn,
		path: conf,
		cb:   client.configChanged,
	}
	go client.configWatcher.watch()
}

func (client *JonesClient) configChanged(data []byte) {
	if len(data) > 0 {
		json.Unmarshal(data, &client.config)
	}
	if !client.synced {
		client.synced = true
		client.wg.Done()
	}
}

func (client *JonesClient) Get(key string) interface{} {
	return client.config[key]
}

func New(service string) *JonesClient {
	client := &JonesClient{service: service}
	client.hostname, _ = os.Hostname()
	return client
}
