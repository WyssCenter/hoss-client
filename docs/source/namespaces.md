# Namespaces

Namespaces are an abstraction around object store buckets. This removes the complexity and confusion around where
data is stored and how to interact with the object store. From the perspective of this library, a namespace can
be thought of as simply a container that groups together unrelated [datasets](datasets.md).

Namespaces can be linked together via a 1-way or 2-way sync configuration. Once a namespace is configured for syncing,
datasets inside the namespace can enable 1-way or 2-way syncing (i.e. a 2-way dataset sync requires a 2-way namespace
sync configuration).


## Managing Namespaces

For most users, you'll typically list or directly load existing {py:class}`hoss.namespace.Namespace` instances.

```python
>>> import hoss
>>> server = hoss.connect("https://hoss.mycompany.com")

>>> server_local.list_namespaces()
[<Namespace: default - Default namespace>]

>>> ns = server_local.get_namespace("default")
```

Once you have a {py:class}`hoss.namespace.Namespace` instance, you can interact with that namespace and the 
[datasets](datasets.md) it contains.


Only users with the `admin` role can create namespaces. This can be done via 
{py:class}`hoss.core.CoreService.create_namespace` function.

```python
import hoss
server = hoss.connect("https://hoss.mycompany.com")
ns = server.create_namespace("test-namespace", "A namespace for testing",
                             "on-premise-1", "my-bucket")
```

Admins can also delete namespaces via the {py:class}`hoss.core.CoreService.delete_namespace` function.

```python
import hoss
server = hoss.connect("https://hoss.mycompany.com")
server.delete_namespace("test-namespace")
```

```{note}
A namespace must be empty before deleting. This means you should delete all datasets in the namespace and disable
syncing before attempting to delete.
```



## Namespace Sync Configuration

### Viewing Namespace Sync Configuration

You can list a namespace's sync configuration using the {py:class}`hoss.namespace.Namespace.get_sync_configuration`
function. This will return a list of dictionaries containing the sync targets. 

```python
>>> import hoss
>>> server = hoss.connect("https://hoss.local-server.com")
>>> ns = server.get_namespace("default")
>>> ns.get_sync_configuration()
[{"target_core_service": "https://hoss.remote-server.com/core/v1", "target_namespace": "default", "sync_type": "duplex"}]
```

The `target_core_service` is the URI for the Hoss core API service. This typically is another server, but a Hoss server
does support syncing to itself. There are use cases where this would be useful (e.g. moving data to different buckets
in different object store, moving data to different buckets with different properties, testing, etc.).

The `target_namespace` is the name of the namespace to which datasets will be synced. Typically this is the same name
as the current namespace, minimizing code changes for developers moving between servers, but it can be different.

The `sync_type` indicates if the sync configuration is 1-way (`simplex`) or 2-way (`duplex`). A 1-way sync configuration
will only allow datasets to have 1-way syncing enabled. A 2-way sync configuration will allow datasets to have either
1-way or 2-way syncing.

In 1-way syncing, data written or deleted from **this** namespace is propagated to the target namespace.

In 2-way syncing, data written or deleted from **either** namespace will be propagated.

### Modifying Namespace Sync Configuration

Namespace sync configurations can only be modified by administrators.

It is important to note that the API currently supports configuring multiple sync targets for a single namespace. 
This capability is not fully supported and may result in unexpected behavior. 
You should only configure a single sync target per namespace.

To add a sync target to a namespace, use the {py:class}`hoss.namespace.Namespace.enable_sync_target` function.

```python
import hoss
server = hoss.connect("https://hoss.local-server.com")
ns = server.get_namespace("default")
ns.enable_sync_target("https://hoss.remote-server.com/core/v1", "duplex", "my-namespace")
```

To remove a sync target from a namespace, use the {py:class}`hoss.namespace.Namespace.disable_sync_target` function.

```python
import hoss
server = hoss.connect("https://hoss.local-server.com")
ns = server.get_namespace("default")
ns.disable_sync_target("https://hoss.remote-server.com/core/v1", "my-namespace")
```

