# Working With Data
This library provides familiar interfaces to interact with data. It automatically handles credentials and making
requests to the underlying object storage, leaving you free to think about your real work.

The primary interface to data is the {py:class}`hoss.ref.DatasetRef` class. `DatasetRef` instances are references
to objects in the dataset. `DatasetRefs` have properties like `size_bytes`, `metadata`, `etag`, and `last_modified` that
are loaded and available without actually fetching any data.

Note, there is no physical representation of "directories" in an object store. This is done virtually by 
convention, with trailing `/` character representing a directory or levels in a hierarchy when in an object key.

## Reading and Writing Data

`DatasetRef`s can be created using the `/` operator, similar to Python's `pathlib`. You can then do common
file-like operations.

Assuming you have loaded a {py:class}`hoss.dataset.Dataset` into `ds`
```python
>>> ref1 = ds / "file1.bin"
>>> ref2 = ds / "folder1" / "file2.bin"
>>> ref_dir = ds / "folder1"

>>> ref1.exists()
True

>>> ref2.is_file()
True

>>> ref_dir.is_dir()
True
```

### Text Interface
You can read and write text data to `DatasetRefs`

```python
>>> ref1 = ds / "file1.txt"
>>> ref1.write_text("Hello, world!")
>>> ref1.read_text()
Hello, world!
```

### Binary Interface
You can read and write binary data to `DatasetRefs`

```python
>>> ref1 = ds / "file1.txt"
>>> ref1.write_bytes(b"abcd1234")
>>> ref1.read_bytes()
b'abcd1234'
```


### File Interface
You can directly read and write from and to local files. This method supports both absolute paths to files
or file handles. If a file handle is provided, it must be in binary mode.

Write contents of the local file `file1.bin` into the ref.
```python
filename = "/path/to/file1.bin"
ref1 = ds / "file1.bin"
ref1.write_from(filename)
```

Read the contents of the ref into the local file `file1.bin`
```python
filename = "/path/to/file1.bin"
ref1 = ds / "file1.bin"
ref1.read_to(filename)
```

### Context Manager
A context manager interface is available, making it easy to drop the client library into existing
code.

```python
ref1 = ds / "file1.bin"
with ref1.open('rt') as fh:
    data = fh.read()
```

### Deleting Data
The object that is referenced by a `DatasetRef` can be deleted in the object store using the `unlink` and 
`remove` functions.

```python
>>> ref1 = ds / "file1.bin"

>>> ref1.exists()
True

>>> ref1.remove()

>>> ref1.exists()
False
```

## Iterating Through Objects
There are several methods to iterate through files in a dataset. Depending on the number of files in a dataset
this can take a long time depending on which method is used.

A `glob` interface is available that makes it easy to iterate through all or parts of a directory tree, look
for files that match some sort of pattern (e.g. a file extension), and other useful patterns.

```python
>>> for f in ds.glob("*"):
>>> ... print(f)
<DatasetRef: example-ds/folder1/>
<DatasetRef: example-ds/my-file.bin>
<DatasetRef: example-ds/my-file.txt>
```


```python
>>> for f in ds.glob("my-file*"):
>>> ... print(f)
<DatasetRef: example-ds/my-file.bin>
<DatasetRef: example-ds/my-file.txt>
```

```python
>>> for f in ds.glob("**/my-file*"):
>>> ... print(f)
<DatasetRef: example-ds/folder1/my-file1.bin>
<DatasetRef: example-ds/folder1/my-file2.txt>
<DatasetRef: example-ds/folder1/my-file3.bin>
<DatasetRef: example-ds/my-file.bin>
<DatasetRef: example-ds/my-file.txt>
```

```python
>>> for f in ds.glob("**/*.txt"):
>>> ... print(f)
<DatasetRef: example-ds/folder1/my-file2.txt>
<DatasetRef: example-ds/my-file.txt>
```

Alternatively, you can use the `iterdir` method to iterate through a single "directory" if represented by
a ref.

```python
>>> for f in (ds).iterdir():
>>> ... print(f)
<DatasetRef: example-ds/folder1/>
<DatasetRef: example-ds/my-file.bin>
<DatasetRef: example-ds/my-file.txt>
```

```python
>>> for f in (ds / "folder1").iterdir():
>>> ... print(f)
<DatasetRef: example-ds/folder1/my-file1.bin>
<DatasetRef: example-ds/folder1/my-file2.txt>
<DatasetRef: example-ds/folder1/my-file3.bin>
```

## Searching Objects
You can search for objects via metadata key-value pairs. Search can be limited to a namespace or a dataset. 
Currently only exact matches on key-value pairs are supported.

Available arguments to the search methods:
- `metadata`: dictionary of key-value pairs that must match exactly. Empty dict will return all objects.
- `namespace`: name of namespace to filter results
- `dataset`: name of dataset to filter results (namespace must be set along with dataset to be valid)
- `modified_before`: datetime string format `2006-01-02T15:04:05.000Z` to filter results
- `modified_after`: datetime string format `2006-01-02T15:04:05.000Z` to filter results
- `limit`: number of results to return
- `offset`: starting point for the response, indexed into the total number of results

The {py:class}`hoss.core.CoreService.search` method will return raw responses.

```python
>>> server = hoss.connect('https://hoss.myserver.com')
>>> server.search({'foo': 'bar'})
[{'uri': 'hoss+https://hoss.myserver.com:default:example-ds/folder1/my-file1.bin',
  'file_path': 'folder1/my-file1.bin',
  'dataset': 'example-ds',
  'namespace': 'default',
  'last_modified_date': '2021-12-14T18:21:40.693Z',
  'size_bytes': 123345,
  'metadata': [{'foo': 'bar'}, {'fizz': 'buzz'}]},
 {'uri': 'hoss+https://hoss.myserver.com:default:example-ds/folder1/my-file2.txt',
  'file_path': 'folder1/my-file2.txt',
  'dataset': 'example-ds',
  'namespace': 'default',
  'last_modified_date': '2021-12-14T18:21:40.733Z',
  'size_bytes': 12,
  'metadata': [{'fizz': 'other'}, {'foo': 'bar'}]},
 {'uri': 'hoss+https://hoss.myserver.com:default:example-ds/folder1/my-file3.bin',
  'file_path': 'folder1/my-file3.bin',
  'dataset': 'example-ds',
  'namespace': 'default',
  'last_modified_date': '2021-12-14T18:21:40.760Z',
  'size_bytes': 435,
  'metadata': [{'foo': 'bar'}]}]
```

The {py:class}`hoss.core.CoreService.search_refs` method will return {py:class}`hoss.ref.DatasetRef` instances
that you can directly interact with.


```python
>>> server = hoss.connect('https://hoss.myserver.com')
>>> server.search_refs({'foo': 'bar'})
[<DatasetRef: example-ds/folder1/my-file1.bin>,
<DatasetRef: example-ds/folder1/my-file2.txt,
<DatasetRef: example-ds/folder1/my-file3.bin>]
```

## Hoss URI
The Hoss generates unique URIs for every object that is stored. This lets you directly reference and load
individual objects.

The URI format is `hoss+<server>:<namespace>:<dataset>/<object key>`

You can access the URI from any ref via the `uri` property:

```python
>>> ref1 = ds / "my-file.bin"
>>> ref1.uri
'hoss+https://hoss.myserver.com:default:example-ds/my-file.bin'
```

Once you have a URI, you can directly load the associated {py:class}`hoss.ref.DatasetRef` instance
using the {py:class}`hoss.resolve` method.

```python
>>> hoss.resolve('hoss+https://hoss.myserver.com:default:example-ds/my-file.bin')
<DatasetRef: example-ds/my-file.bin>
```
