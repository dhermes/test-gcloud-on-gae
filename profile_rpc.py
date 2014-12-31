# This was run against version 0.3.0.

import datetime
import time

from gcloud import datastore
from gcloud.datastore import datastore_v1_pb2 as datastore_pb
from gcloud.datastore import helpers
from gcloud.datastore import key


PRIVATE_KEY_PATH = 'Foo'
CLIENT_EMAIL = 'Bar'
DATASET_ID = 'Baz'
DATASET = datastore.get_dataset(DATASET_ID, CLIENT_EMAIL, PRIVATE_KEY_PATH)
CONNECTION = DATASET.connection()
PARTIAL_KEY_PB = key.Key(path=[{'kind': 'Foo'}]).to_protobuf()

BASE_DATA = {
    'now': datetime.datetime.utcnow(),
    'nickname': 'Jeff',
    'email': 'jeff@email.com',
    'user_id': '123456789012345678901',
}

FANCY_DATASET_ID = 's~' + DATASET_ID


def check_key_pb(key_pb):
    if (key_pb.partition_id.dataset_id != FANCY_DATASET_ID or
        len(key_pb.path_element) != 1 or
        key_pb.path_element[0].kind != u'Foo'):
        raise ValueError(key_pb)


def save_fresh():
    start = time.time()
    key_pb = CONNECTION.save_entity(
        dataset_id=DATASET_ID,
        key_pb=PARTIAL_KEY_PB,
        properties=BASE_DATA,
        exclude_from_indexes=frozenset(),
    )
    duration = time.time() - start

    check_key_pb(key_pb)
    return duration


MUTATION = CONNECTION.mutation()
INSERT_AUTO = MUTATION.insert_auto_id.add()
INSERT_AUTO.key.CopyFrom(PARTIAL_KEY_PB)
for name, value in BASE_DATA.items():
    prop = INSERT_AUTO.property.add()
    # Set the name of the property.
    prop.name = name
    prop.value

    # Set the appropriate value.
    helpers._set_protobuf_value(prop.value, value)


def save_entity_fresh():
    start = time.time()
    result = CONNECTION.commit(DATASET_ID, MUTATION)
    duration = time.time() - start

    key_pb = result.insert_auto_id_key[0]
    check_key_pb(key_pb)
    return duration


COMMIT_REQUEST = datastore_pb.CommitRequest()
COMMIT_REQUEST.mode = datastore_pb.CommitRequest.NON_TRANSACTIONAL
COMMIT_REQUEST.mutation.CopyFrom(MUTATION)


def commit_fresh():
    start = time.time()
    response = CONNECTION._rpc(DATASET_ID, 'commit', COMMIT_REQUEST,
                               datastore_pb.CommitResponse)
    duration = time.time() - start

    key_pb = response.mutation_result.insert_auto_id_key[0]
    check_key_pb(key_pb)
    return duration


REQUEST_PAYLOAD = COMMIT_REQUEST.SerializeToString()


def _rpc_fresh():
    start = time.time()
    response = CONNECTION._request(
        dataset_id=DATASET_ID,
        method='commit',
        data=REQUEST_PAYLOAD,
    )
    duration = time.time() - start

    pb_resp = datastore_pb.CommitResponse.FromString(response)
    key_pb = pb_resp.mutation_result.insert_auto_id_key[0]
    check_key_pb(key_pb)
    return duration


REQUEST_HEADERS = {
    'Content-Type': 'application/x-protobuf',
    'Content-Length': str(len(REQUEST_PAYLOAD)),
    'User-Agent': 'gcloud-python/0.3.0',
}
REQUEST_URI = CONNECTION.build_api_url(
    dataset_id=DATASET_ID,
    method='commit',
)
HTTP = CONNECTION.http


def _request_fresh():
    start = time.time()
    response_headers, content = HTTP.request(
        uri=REQUEST_URI,
        method='POST',
        headers=REQUEST_HEADERS,
        body=REQUEST_PAYLOAD,
    )
    duration = time.time() - start
    if response_headers['status'] != '200':
        msg = 'Bad status: %s' % (response_headers['status'],)
        raise ValueError(msg)

    pb_resp = datastore_pb.CommitResponse.FromString(content)
    key_pb = pb_resp.mutation_result.insert_auto_id_key[0]
    check_key_pb(key_pb)
    return duration


def run_with_sleep(user_method):
    durations = []
    for i in range(5):
        time.sleep(3)
        durations.append(user_method())
    print 'Method call durations:'
    print ', '.join(['%g' % (duration,) for duration in durations])


def main():
    user_methods = (
        save_fresh,
        save_entity_fresh,
        commit_fresh,
        _rpc_fresh,
        _request_fresh,
    )

    print 'Performing throwaway request to warm up the backend.'
    duration = save_fresh()
    print 'Warm-up took %g seconds, sleeping for 3 more.' % (duration,)
    time.sleep(3)
    print 'Will perform each method 5 times, with 3 seconds sleep between.'

    for user_method in user_methods:
        print '=' * 60
        print 'Running method: %s()' % (user_method.__name__,)
        run_with_sleep(user_method)


if __name__ == '__main__':
    main()
