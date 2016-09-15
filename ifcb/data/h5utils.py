from contextlib import contextmanager

import numpy as np
import pandas as pd
import h5py as h5

H5_REF_TYPE = h5.special_dtype(ref=h5.Reference)

def clear_h5_group(h5group):
    """delete all keys and attrs from an h5.Group.
    is this a good idea?"""
    for k in h5group.keys(): del h5group[k]
    for k in h5group.attrs.keys(): del h5group.attrs[k]

class hdfopen(object):
    """context mgr: open an hdf5 group from a file or other group
    parameters:
    path - path to HDF5 file, or open HDF5 group
    group - for HDF5 file paths, the group path to return (optional);
    for groups, a subgroup to require (optional)"""
    def __init__(self, path, group=None, replace=None):
        if isinstance(path, h5.Group):
            if group is not None:
                self.group = path.require_group(group)
            else:
                self.group = path
            if replace:
                clear_h5_group(self.group)
            self._file = None
        else:
            mode = 'w' if replace else 'r+'
            self._file = h5.File(path, mode)
            if group is not None:
                self.group = self._file.require_group(group)
            else:
                self.group = self._file
    def close(self):
        if self._file is not None:
            self._file.close()
    def __enter__(self, *args, **kw):
        return self.group
    def __exit__(self, *args):
        self.close()
        pass

"""
Layout of Pandas DataFrame / Series representation
- {path} (group): the group containing the dataframe
- {path}.ptype (attribute): 'DataFrame' / 'Series'
- {path}/columns (dataset): 1d array of references to column data
- {path}/columns.names (attribute, optional): 1d array of column names
- {path}/{n} (dataset): 1d array of data for column n
- {path}/index (dataset): 1d array of data for dataframe index
- {path}/index.name (attribute, optional): name of index

Series are represented like single-column DataFrames
"""

def pd2hdf(group, df, **kw):
    """kw params used for all dataset creation operations"""
    group.attrs['ptype'] = 'DataFrame'
    refs = []
    for i in range(len(df.columns)):
        c = group.create_dataset(str(i), data=df.iloc[:,i], **kw)
        refs.append(c.ref)
    cols = group.create_dataset('columns', data=refs, dtype=H5_REF_TYPE)
    cols.attrs['names'] = list(df.columns)
    ix = group.create_dataset('index', data=df.index, **kw)
    if df.index.name is not None:
        ix.attrs['name'] = df.index.name

def hdf2pd(group):
    assert group.attrs['ptype'] == 'DataFrame'
    index = group['index']
    index_name = index.attrs.get('name',None)
    col_refs = group['columns']
    col_data = [np.array(group[r]) for r in col_refs]
    # note: the below assumes that no column names mean use numeric oness
    col_names = col_refs.attrs.get('names', range(len(col_refs)))
    data = { k: v for k, v in zip(col_names, col_data) }
    index = pd.Series(index, name=index_name)
    return pd.DataFrame(data=data, index=index, columns=col_names)
