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

Authentication
==============

Make sure to visit the APIs console at

```
https://console.developers.google.com/project/<YOUR-PROJECT>/apiui/api
```

and enable "Google Cloud Datastore API".

In addition, make sure the App Engine Service Account has permissions
as a member of your project:

```
https://console.developers.google.com/project/<YOUR-PROJECT>/permissions
```

and add the email

```
<YOUR-PROJECT>@appspot.gserviceaccount.com
```

Due to the lines

```python
from google.appengine.api.app_identity import get_application_id
...
APP_NAME = get_application_id()
...
if APP_NAME is None:
    DATASET = None
else:
    DATASET = CONNECTION.dataset(APP_NAME)
```

Hacks Used
==========

- [Disabling][3] GCE environ check since we know we're on App Engine.
- Using [`gae-pytz`][5] and [Updating][4] `pytz` imports for App Engine.
- [Removing][6] dependency on `pkg_resources.get_distribution` for
  application version (used in User Agent).

[1]: https://www.simonmweber.com/2013/06/18/python-protobuf-on-app-engine.html
[2]: https://github.com/google/protobuf
[3]: https://github.com/dhermes/test-protobuf-on-gae/commit/365d51240452259d97ed583c8f07746b9ca6eae5
[4]: https://github.com/dhermes/test-protobuf-on-gae/commit/f7f05bb1fe710128b8e4842da338e1a2d1c5c5c8
[5]: https://code.google.com/p/gae-pytz/
[6]: https://github.com/dhermes/test-protobuf-on-gae/commit/4457b2f846ac8f65f38e5c38fbf2258a60a67ebe
