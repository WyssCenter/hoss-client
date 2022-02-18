# Servers

## Connecting
In most cases, you'll always start by connecting to a server. This is done by simply providing the URL for the server,
to the {py:class}`hoss.connect` function. This will return a {py:class}`hoss.core.CoreService` instance, 
which is used to interact with a Hoss server's API.

```python
import hoss
server = hoss.connect("https://hoss.mycompany.com")
```  

## Working with Multiple Servers
Often, you will be working with two or more Hoss servers that are linked together for syncing.

Linked servers enable hybrid workflows where data is synchronized and available in multiple locations. This is 
useful for various scenarios such as collaboration, analytics on hybrid infrastructure, and distributed data generation.

When multiple servers are configured, it is important to understand how the authentication system is configured. There
will either be a single auth service in use or each server will have its own. You can tell how your system is configured
by looking at the domain name of the login page. If the domain name is always the same no matter which server you
are logging into, then a single auth service is in use. If the domain name changes, then multiple auth services
are in use.

### Single Auth Service Configuration
If a single auth service is in use there is nothing special you have to do. The client library will automatically
look up the auth service and exchange your PAT for Hoss API credentials that will work with all linked servers.
Object store (i.e. S3, minio) credentials are automatically generated and renewed as needed.

### Multiple Auth Services Configuration

If multiple auth services are in use there are additional considerations. Since your PAT will only be known by the
server that is running the auth service there are two options. You can either use multiple PATs or explicitly set the
{py:class}`hoss.auth.AuthService` instance.

To use multiple PATs, create a PAT in each server you want to connect to. Then you must remember to set the `HOSS_PAT`
environment variable to the proper PAT when connecting to a server.

Alternatively you can explicitly set the {py:class}`hoss.auth.AuthService` instance. In this case, you only need one
PAT in one server. You'll always connect to that server first, and then use the {py:class}`hoss.auth.AuthService` 
instance that is created in other {py:class}`hoss.connect` calls.

```python
import hoss
primary_server = hoss.connect("https://hoss.my-on-prem-domain.com")
secondary_server = hoss.connect("https://hoss.my-cloud-domain.com", 
                                auth_instance=primary_server.auth)
```

In both cases, the client library will exchange your PAT for Hoss API credentials and object store (i.e. S3, minio)
credentials will be automatically generated and renewed as needed.
 

## Switching Between Servers
One of the primary benefits of syncing data is that your analysis code will work in multiple locations 
with minimal changes. 

A typical configuration could be the following:

- A server running at `https://hoss.my-on-prem-domain.com`.
- A server running at `https://hoss.my-cloud-domain.com`
- A namespace named `default` exists in both servers. 
- The `default` namespaces are linked together via 2-way syncing.

In this setup, you can create a dataset that has 2-way syncing enabled. Now, data written when connected to either
server will be available at both locations.

The only change required to run your code using data from a different location is to change the {py:class}`hoss.connect`
call. The client library will automatically get required credentials and configure connections
to the underlying object storage system. Your code doesn't have to know how to connect to S3 or minIO, which
bucket to point to, what policies are needed, etc. All this is automatically configured for you.

In this example, you can work on-premise like this:
```python
import hoss
server = hoss.connect("https://hoss.my-on-prem-domain.com")
ns = server.get_namespace("default")
ds = ns.get_dataset("my-dataset")
...
```  

And move your code to a cloud instance then switch the data source by just pointing to a different server:
```python
import hoss
server = hoss.connect("https://hoss.my-cloud-domain.com")
ns = server.get_namespace("default")
ds = ns.get_dataset("my-dataset")
...
```  


