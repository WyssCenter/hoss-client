# Datasets
Datasets are a collection of related objects, or files. Permissions are applied to users and groups to grant access
to the dataset and the objects it contains. Objects can be searched based on metadata and interacted with using
familiar file-based interfaces.

## Managing Datasets

```{note} 
A user must have the `admin` or `privileged` role to create and delete datasets
```

Datasets within a namespace are managed from its respective {py:class}`hoss.namespace.Namespace` instance. You must
load the namespace that contains the dataset you wish to interact with first.

Users with the the `admin` or `privileged` role can create and delete datasets. 

```python
import hoss
server = hoss.connect("https://hoss.local-server.com")
ns = server.get_namespace("default")

# Create a dataset
ds = ns.create_dataset("my-dataset", "A good description of this dataset")

# Delete the dataset
ns.delete_dataset("my-dataset")
```

All users can list and get {py:class}`hoss.dataset.Dataset` instances.

```python
>>> import hoss
>>> server = hoss.connect("https://hoss.local-server.com")
>>> ns = server.get_namespace("default")

>>> ns.list_datasets()
[<Dataset: <Namespace: default - Default namespace> - my-dataset>, <Dataset: <Namespace: default - Default namespace> - another-dataset>]

>>> ds = ns.get_dataset("my-dataset")

```

## Dataset Deletion
When a dataset is deleted, it is first marked for deletion. Depending on your server configuration, after some 
fixed amount of time (e.g 48 hours), the dataset will be deleted. When the delete occurs, all objects within that 
dataset are removed from the bucket that backs the namespace. You can check the delete delay using the `discovery`
endpoint: `<server_url>/core/v1/discover`

You can check the state of a dataset via the `delete_status` field on any {py:class}`hoss.dataset.Dataset` instance. If
it is `SCHEDULED` you can see when it will be deleted via the `delete_on` field. If it is `IN_PROGRESS` the delete
is running. If it is `ERROR`, an error occured while being deleted and you should contact an administrator.

Additionally, users with the `admin` role can use the {py:class}`hoss.namespace.Namespace.restore_dataset` function
to "unmark" a dataset for delete. This can be done at any time while the dataset is still in the `SCHEDULED` state.

## Dataset Permissions
Once a dataset is created, only the user who created it will have access. To share or collaborate with a dataset, you
must add additional permissions.

Permissions can be applied to individual users and [groups](groups.md) of users.

Read-only permissions will allow the user or group to see the dataset and read objects from it. They will not be able
to write or delete data.

Read-write permissions will allow the user or group to both not only access the dataset and read data, but also write
and delete data.

Assuming you have loaded a {py:class}`hoss.dataset.Dataset` instance by doing something like this:
```python
import hoss
server = hoss.connect("https://hoss.local-server.com")
ns = server.get_namespace("default")
ds = ns.get_dataset("my-dataset")
```

To add read permissions to a user with the username `user-1` you would do the following:
```python
ds.set_user_permission("user-1", "r")
```

To add read-write permissions to a user with the username `user-2` you would do the following:
```python
ds.set_user_permission("user-2", "rw")
```

To remove access for a user with the username `user-1` you would do the following:
```python
ds.set_user_permission("user-1", None)
```

To add read permissions to a group with the group name `test-user-group` you would do the following:
```python
ds.set_group_permission("test-user-group", "r")
```

To add read-write permissions to a group with the group name `test-user-group` you would do the following:
```python
ds.set_group_permission("test-user-group", "rw")
```

To remove access for a group with the group name `test-user-group` you would do the following:
```python
ds.set_group_permission("test-user-group", None)
```


## Dataset Syncing
Once a [namespace](namespaces.md) has been configured for syncing, you will be able to enable syncing on individual
datasets. The namespace determines the target server & namespace to which the dataset will be synced. All datasets
in a namespace will sync to the same target server & namespace.

If the namespace supports 2-way syncing, you will be able to enable 1-way (simplex) or 2-way (duplex) syncing on the
dataset. If the namespace only supports 1-way syncing, you will only be able enable 1-way syncing on the dataset.

When dataset syncing is enabled, the dataset is automatically created for you in the target namespace. If any data
already exists in the dataset, it will be synced. After this setup process, any write or delete operations will be
replicated (unless a sync policy rejects the operation as described below.)

```{note} 
A user must have the `admin` or `privileged` role to manage dataset syncing
```

```python
import hoss
>>> server = hoss.connect("https://hoss.local-server.com")
>>> ns = server.get_namespace("default")
>>> ds = ns.get_dataset("my-dataset")

>>> ds.is_sync_enabled()
False

>>> ds.enable_sync("duplex")

>>> ds.is_sync_enabled()
True

>>> ds.disable_sync()

>>> ds.is_sync_enabled()
False
```

### Sync Policies

By default, all write and delete operations will be synchronized. You can optionally specify a sync policy that will filter
which objects are synchronized. If omitted, the default empty policy is used that allows the default behavior. 

The policy structure is fully documented in the 
[sync policy spec](https://github.com/gigantum/hybrid-object-store/blob/main/resources/docs/server/sync_policy.md), 
but is summarized below. You can manually enter policies in the UI, or provide them to the
{py:class}`hoss.dataset.Dataset.enable_sync` method.

The sync policy is as JSON document containing Statements which contain Conditions, whose logic will be combined together
for a final decision on if an object should be synced. If the logical operations evaluate to `true` the object will
by synced, if `false` it will not.

The default "open" policy is: 

```json
{
  "Version": "1",
  "Effect": "OR",
  "Statements":[]
}
```

Here, the `Effect` field can be either `OR` or `AND`, and specifies how the result of each Statement is logically combined.
If omitted the default is `OR`.

Statements are JSON objects with the format:

```json
{
  "Id": "AnIdYouMakeUp",
  "Effect": "AND",
  "Conditions": []
}
```
The `Id` field is a string that you can use to identify Statements. The Hoss does not interpret these in any way.

The `Effect` field can be either `OR` or `AND`, and specifies how the result of each Condition is logically combined.
If omitted the default is `AND`.

Conditions are JSON objects that define a logical condition with the format:

```json
{
  "Left": <string>,
  "Right": <string> or <int>,
  "Operator": <string>,
}
```

The `Left` field can have one of the following values:
* `"event:operation"`: The type of notification event generated for the file
  - The value is either `"PUT"` (for create or update) or `"DELETE"` (for delete)
* `"object:key"`: The key of the object that is the focus of the notification message
* `"object:size"`: The size of the object (in bytes) that is the focus of the notification message
* `"object:metadata"`: The object's metadata dictionary
  - Used with the `"has"` operator to check if a metadata key exists
* `"object:metadata:<key>"`: The key of the object's metadata to use in the conditional
  - `"<key>"`: Is a string containing the name of the metadata key
  - All metadata values are strings

The `Right` field can have one of the following values:
* `""`: An empty string can be used to verify that a metadata value doesn't exist
* `"<glob>"`: A glob expression to match against the `Left` operand
  - Only supports `"=="` and `"!="` operators
* `<number>: An integer or float number

The `Operator` field can have one of the following values:
* `"=="`: Returns true if the two operands are equal
* `"!="`: Returns true if the two operands are not equal
* `">"`: Returns true if the left operand is greater than the right operand
* `"<"`: Returns true if the left operand is less than the right operand
* `">="`: Returns true if the left operand is greater than or equal to the right operand
* `"<="`: Returns true if the left operand is less than or equal to the right operand
* `"has"`: Returns true if the left operand dictionary contains the right operand key

To implement a simple policy that skips syncing large files over 1GB completely using the `hoss` package, you could:

```python
import hoss
server = hoss.connect("https://hoss.local-server.com")
ns = server.get_namespace("default")
ds = ns.get_dataset("my-dataset")

policy = {"Version": "1", "Statements": []}
statement = dict()
statement["Id"] = "NoLargeFiles"
statement["Conditions"] = [
        {
            "Left": "object:size",
            "Right": 1000000000,
            "Operator": "<"
        }
    ]
policy['Statements'].append(statement)
ds.enable_sync("simplex", sync_policy=policy)
```

### Example Sync Policies
This section some example sync policies to help illustrate how to use the various fields and what is possible.

**Filter on file name**

This policy uses the `object:key` value to compare against the object's key. The `*.raw` string is a glob expression
that would return any file that ends with the `.raw` extension. So when paired with the `!=` operator, this sync
policy would **not** sync any file that ends in with a `.raw` exension.

```json
{
  "Version": "1",
  "Statements": [
    {
      "Id": "IgnoreRaw",
      "Conditions": [
        {
          "Left": "object:key",
          "Right": "*.raw",
          "Operator": "!="
        }
      ]
    }
  ]
}
```

**Filter on operation**

This policy uses the `event:operation` value to compare against the type of operation; a write (`PUT`) or a delete (`DELETE`).
The policy will only sync write events and will ignore delete events. This is a good policy if you want to sync
all data to the cloud but only keep a subset locally.

```json
{
  "Version": "1",
  "Statements": [
    {
      "Id": "OnlyPuts",
      "Conditions": [
        {
          "Left": "event:operation",
          "Right": "PUT",
          "Operator": "=="
        }
      ]
    }
  ]
}
```


**Filter on file size**

Sometimes you may want to control what is sync based on file size. This policy uses the `object:size` value to ignore
large files. The `object:size` value is the size of the object in bytes.

```json
{
  "Version": "1",
  "Statements": [
    {
      "Id": "SmallFilesOnly",
      "Conditions": [
        {
          "Left": "object:size",
          "Right": 10000,
          "Operator": "<"
        }
      ]
    }
  ]
}
```

**Filter on a metadata key existing**

This policy makes sure an object has a metadata key. If they key is present, regardless of it's value, the file will
be synced. This uses the special `has` operator that is only available with the `object:metadata` value. 

```json
{
  "Version": "1",
  "Statements": [
    {
      "Id": "MustHaveTag",
      "Conditions": [
        {
          "Left": "object:metadata",
          "Right": "sync-me",
          "Operator": "has"
        }
      ]
    }
  ]
}
```

**Filter on a metadata value**

This policy makes sure an object has specific metadata key-value pair by using the `object:metadata:<key>` value. 
You can use glob expressions here too for a more flexible matching.

```json
{
  "Version": "1",
  "Statements": [
    {
      "Id": "MatchValue",
      "Conditions": [
        {
          "Left": "object:metadata:my-key",
          "Right": "my-val-1",
          "Operator": "=="
        }
      ]
    }
  ]
}
```

**Using Multiple Conditions**

You can use multiple conditions to build more complex logical operations. Here we only sync files that are within
a range of file sizes. 

```json
{
  "Version": "1",
  "Statements": [
    {
      "Id": "MediumFilesOnly",
      "Effect": "AND",
      "Conditions": [
        {
          "Left": "object:size",
          "Right": 100000,
          "Operator": "<"
        },
        {
          "Left": "object:size",
          "Right": 5000,
          "Operator": ">"
        }
      ]
    }
  ]
}
```

**Using Multiple Statements**

You can also multiple Statements to build more complex logical operations. Here we only sync files that are either small
or have a specified metadata key. When combined with multiple conditions you can typically craft any required logical
condition. 

```json
{
  "Version": "1",
  "Effect": "OR",
  "Statements": [
    {
      "Id": "HaveKey",
      "Conditions": [
        {
          "Left": "object:metadata",
          "Right": "key1",
          "Operator": "has"
        }
      ]
    },
    {
      "Id": "IsSmall",
      "Conditions": [
        {
          "Left": "object:size",
          "Right": 500,
          "Operator": "<"
        }
      ]
    }
  ]
}
```

## Suggesting Metadata Keys and Values
You can get suggestions for keys or values based on existing metadata key-value pairs within a dataset.

Available arguments to the suggest methods:
- `key`: for value suggestions only, a key must be specified to filter suggestions.
- `prefix`: string prefix to base suggestions on. Suggestions will include keys or values beginning with this prefix.
- `limit`: number of objects to return suggestions. The exact number of suggestions may vary due to de-duplication of results and multiple matching keys or values within a single object.

The {py:class}`hoss.dataset.Dataset.suggest_keys` method will return suggestions for keys within a dataset, and the {py:class}`hoss.dataset.Dataset.suggest_values` method will return suggestions for values within a dataset for a given key.

```python
>>> server = hoss.connect('https://hoss.myserver.com')
>>> ns = server.get_namespace("default")
>>> ds = ns.get_dataset("my-dataset")
>>> ds.suggest_keys('f')
['foo', 'fizz']
>>> ds.suggest_values('fizz', 'bu')
['buzz']
```
