cassandradl.CassandraDataset class
==================================

The only class that the user needs to interact with, in order to use
the Cassandra Data Loader, is ``cassandra_dataset.CassandraDataset``.

.. autoapimethod:: cassandradl.CassandraDataset.__init__

Th class must be initialized with the credentials and the hostname for
connecting to the Cassandra DB, as in the following example::

  from cassandra_dataset import CassandraDataset
  from cassandra.auth import PlainTextAuthProvider
  
  ## Cassandra connection parameters
  ap = PlainTextAuthProvider(username='user', password='pass')
  cd = CassandraDataset(ap, ['cassandra-db'])

  
The next step is initializing a list manager, reading metadata from
the DB.

.. autoapimethod:: cassandradl.CassandraDataset.init_listmanager
.. autoapimethod:: cassandradl.CassandraDataset.read_rows_from_db
.. autoapimethod:: cassandradl.CassandraDataset.init_datatable

For example::

  cd.init_listmanager(
    table='patches.metadata_by_nat',
    id_col='patch_id',
    label_col="label",
    grouping_cols=["patient_id"],
    num_classes=2
  )
  cd.read_rows_from_db()
  cd.init_datatable(
    table='patches.data_by_uuid'
  )
  
The parameter ``grouping_cols`` (optionally) specifies the columns by
which the images should be grouped, before dividing the groups among
the splits. For example, in digital pathology contexts we typically
want that all images of the same patient go either into the training
or the validation set. If ``grouping_cols`` is not specified, then
each image forms a group by itself (i.e., a singlet).

After the list manager has been initialized and the metadata has been
read from the DB, the splits can be created automatically, using the
``split_setup`` method.

.. autoapimethod:: cassandradl.CassandraDataset.split_setup

For example, creating three splits (training, validation and test),
with a total of one million patches and proportions respectively 70%,
20% and 10%::

  cd.split_setup(
    split_ratios=[7,2,1],
    balance=[1,1],
    max_patches=1000000
  )

The option ``balance`` asks the split manager to choose images such as
to achieve a desired balance balance among the classes (in this case 1:1).
In the example, the algorithm will try to fill the training
set with 700,000 images, half of them of class 0 (e.g., normal) and
the other half class 1 (e.g., tumor). If there are not enough images the loader
will choose the maximum value that allows to maintain the desired balance.
  
Same split ratios, but using all the images in the DB and ignoring
the balance among classes::
  
  cd.split_setup(
    split_ratios=[7,2,1],
  )
  
Apply some ECVL augmentations when loading the data::

  training_augs = ecvl.SequentialAugmentationContainer(
      [
          ecvl.AugMirror(0.5),
          ecvl.AugFlip(0.5),
          ecvl.AugRotate([-180, 180]),
      ]
  )
  augs = [training_augs, None, None]
  cd.split_setup(
      split_ratios=[7, 2, 1],
      augs=augs,
  )

Create 10 splits, using a total of one million patches::

  cd.split_setup(
    split_ratios=[1]*10,
    max_patches=1000000
  )

To set the batch size and specify to generate only full batches
(i.e., 32 images also in the last batch)::

  cd.set_batchsize(32, full_batches=True)

Once the splits have been created, they can easily be saved (together
with all the table information), using the ``save_splits`` method and
then reloaded with ``load_splits``.

.. autoapimethod:: cassandradl.CassandraDataset.save_splits
.. autoapimethod:: cassandradl.CassandraDataset.load_splits

For example::
  
  cd.save_splits(
    'splits/1M_3splits.pckl'
  )

And, to load an already existing split file::
  
  from cassandra_dataset import CassandraDataset
  from cassandra.auth import PlainTextAuthProvider
  
  ## Cassandra connection parameters
  ap = PlainTextAuthProvider(username='user', password='pass')
  cd = CassandraDataset(ap, ['cassandra-db'])
  cd.load_splits(
    'splits/1M_3splits.pckl'
  )

  
Once the splits are setup, it is finally possible to load batches of
features and labels and pass them to a DeepHealth application, as
shown in the following example::
  
  epochs = 50
  split = 0 # training
  cd.set_batchsize(32)
  for _ in range(epochs):
      cd.rewind_splits(shuffle=True)
      for _ in range(cd.num_batches[split]):
          x,y = cd.load_batch(split)
          ## feed features and labels to DL engine [...]
  
.. autoapimethod:: cassandradl.CassandraDataset.set_batchsize
.. autoapimethod:: cassandradl.CassandraDataset.rewind_splits
.. autoapiattribute:: cassandradl.CassandraDataset.num_batches
.. autoapimethod:: cassandradl.CassandraDataset.load_batch

