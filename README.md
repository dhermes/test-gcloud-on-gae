test-protobuf-on-gae
====================

Testing Google Protobuf on App Engine

See [import fix][1] and actual [project][2].

Deploying
=========

To deploy set application ID and version environment variables

```
export APP_ID="foo"
export APP_VERSION="bar"
```

and then run

```
make deploy
```


[1]: https://www.simonmweber.com/2013/06/18/python-protobuf-on-app-engine.html
[2]: https://github.com/google/protobuf
