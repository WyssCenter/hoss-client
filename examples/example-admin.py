#!/usr/bin/env python3
import hoss

# A short example showing how to manipulate groups and permissions

if __name__ == '__main__':
    server = hoss.connect("http://localhost")
    ns = server.get_namespace("default")

    print("Existing datasets:")
    print(ns.list_datasets())

    try:
        ds = ns.create_dataset('test1')
    except hoss.AlreadyExistsException:
        ds = ns.get_dataset('test1')
        print("Dataset test1 already exists")

    print("Existing datasets after create operation:")
    print(ns.list_datasets())

    try:
        server.auth.create_group('test_group1', 'test description')
    except hoss.AlreadyExistsException:
        print("Group test_group1 already exists")

    # Working with groups
    server.auth.add_user_to_group('test_group1', 'admin')
    group = server.auth.get_group('test_group1')
    print(group)

    # Working with a dataset
    ds.set_group_permission("test_group1", 'rw')
    ds.display()

    # clean up
    ns.delete_dataset('test1')
