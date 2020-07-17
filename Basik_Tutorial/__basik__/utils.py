

import numpy as np
import math as m
import matplotlib.pyplot as plt
from matplotlib import gridspec
import warnings
from collections import OrderedDict
from pandas import read_csv

try:
    import cPickle as pickle
except ImportError or ModuleNotFoundError:
    import pickle  # all Python has pickle installed.



#------------------------------------------------------------------------------

def load_pickle(file_name):
    '''Loads a serialised/pickled object.
    
    Parameters:
    ----------
    file_name: str
        A file path with .pkl extension as the end.
    
    Raises:
    -------
    TypeError:
        No .pkl extension is present.
        
    Returns:
    --------
    object
    '''
    if file_name[-4:] != '.pkl':
        raise TypeError('file does not contain a .pkl extension')
    
    with open(file_name,'rb') as file:
        object_ = pickle.load(file)
        
    return object_


#------------------------------------------------------------------------------

def load_csv(file_name):
    '''Reads a csv file and presents it as a Pandas DataFrame.
    
    Parameters:
    ----------
    file_name: str
        A file path with .csv extension as the end.
    
    Raises:
    -------
    TypeError:
        No .csv extension is present.
        
    Returns:
    --------
    pandas.core.frame.DataFrame
    '''
    
    if file_name[-4:] != '.csv':
        raise TypeError('file does not contain a .csv extension')
        
    DataFrame = read_csv(file_name)
    
    return DataFrame
    
#------------------------------------------------------------------------------
def unique_legend(axes,loc='best'):
    '''Adds a legend to a matplotlib.axes._subplots.AxesSubplot that does
    not contain any duplicate labels.
    
    Parameters:
    ----------
    axes: matplotlib.axes._subplots.AxesSubplot
        The axes that already contains plots that had a string provided
        for the label argument.
    loc: str
        This is the same loc argument as used by axes.legend(loc='<option>')
    
    Returns:
    --------
    matplotlib.legend.Legend
    
    '''

    # See:
    # https://stackoverflow.com/questions/13588920/stop-matplotlib-repeating-labels-in-legend/13589144
    
    a = axes.get_legend_handles_labels()  # a = [(h1 ... h2) (l1 ... l2)]  non unique
    b = {l:h for h,l in zip(*a)}        # b = {l1:h1, l2:h2}             unique
    c = [*zip(*b.items())]              # c = [(l1 l2) (h1 h2)]
    d = c[::-1]                         # d = [(h1 h2) (l1 l2)]
    return axes.legend(*d)

    
#------------------------------------------------------------------------------


def axes_grid(n_row:int,n_col:int,scale=1):
    
    '''
    Generates a figure and grid similar to that of matplotlib.pyplot.subplots
    with the added benefit that it does not allow for any whitespace between
    plots.
    
    Parameters:
    -----------
    n_row: int
        How many rows in the grid. This must be one or greater.
    n_col: int
        How many columns in the grid. This must be one or greater.
    scale: float
        A positive value (non-zero) where a setting of 1 applies to 
        the standard size.
        A value greater than 1 will lead to a larger plot and vice versa.
        
    
    Raises:
    -------
    ValueError:
        If scale is zero or a negative number.
        If n_row or n_col is not greater or equal to 1.
    TyperError:
        If n_col or n_row is not an int.
    
    Returns:
    --------
    tuple:
        (matplotlib.figure.Figure,
        numpy.ndarray(dtype=object))
    
    Notes:
    ------
    The numpy array contains matplotlib.axes._subplots.AxesSubplot as objects.
    '''

    
    if scale <= 0:
        raise ValueError('scale must be positive and non-zero.')
    if not isinstance(n_row,int):
        raise TypeError('n_row must be an int')
    if not isinstance(n_col,int):
        raise TypeError('n_col must be an int')
    if n_col < 1:
        raise ValueError('n_col >= 1')
    if n_row < 1:
        raise ValueError('n_row >= 1')
    
    
    if scale >= 4:
        message = 'Choosing the scale to be too large '+\
                  'might result in a plot that does not '+\
                  'fit onto the monitor.'
        warnings.warn(message)


    height = (n_row+1)*scale
    width = (n_col+1)*scale
    figure = plt.figure(figsize=(width,height)) 
    
    grid = gridspec.GridSpec(n_row, n_col,
                             wspace=0.0,
                             hspace=0.0, 
                             top=1.-0.5/(n_row+1),
                             bottom=0.5/(n_row+1), 
                             left=0.5/(n_col+1),
                             right=1-0.5/(n_col+1)) 
    
    AxesSubplotArray = np.empty((n_row,n_col),dtype=object)
    for i in range(n_row):
        for j in range(n_col):
            AxesSubplotArray[i,j] = plt.subplot(grid[i,j])
            AxesSubplotArray[i,j].set_xticklabels([])
            AxesSubplotArray[i,j].set_yticklabels([])
            AxesSubplotArray[i,j].set_axis_off()
    
    
    return figure,AxesSubplotArray

#------------------------------------------------------------------------------


def fill_axes_grid(AxesSubplotArray:np.ndarray,
                   image_path_name:str='__basik__/Images/crop1.jpg'):
    
    '''This function takes a numpy array that contains
    matplotlib.axes._subplots.AxesSubplot as its array elements and fills any
    such blank array element with a specified image.
    
    Parameters:
    -----------
    AxesSubplotArray: numpy.ndarray(dtype=object)
        This is a numpy object array that contains 
        matplotlib.axes._subplots.AxesSubplot as its array elements.
        This array can be obtained in a traditional manner as
        >>> n = 3  # arbitrary
        >>> figure,AxesSubplotArray = matplotlib.pyplot.subplots((n,n))
        However, to avoid the issue of white-space in the display, we
        reccommend rather using the axes_grid function to obtain this.
        >>> figure,AxesSubplotArray = __basik__.axes_grid(n,n)
    image_path_name: str
        This should be the path name of the image to be used to fill blank
        space in the figure i.e. fill matplotlib.axes._subplots.AxesSubplot
        objects that have an empty list in their images attribute.
        
    Raises:
    -------
    FileNotFoundError
        If image_path_name is not valid.
    
    Returns:
    --------
    None
    '''
    
    fill_image = plt.imread(image_path_name)
    height,width = np.shape(AxesSubplotArray)
    for i in range(height):
        for j in range(width):
            if not bool(AxesSubplotArray[i,j].images):
                # Empty list
                AxesSubplotArray[i,j].imshow(fill_image)
    
    return None

#------------------------------------------------------------------------------


def rotate_coord(origin:'2D', coord:'2D', angle:'degrees')->'2D':
    
    '''
    Rotates a 2-D point around some chosen origin in a clock-wise direction.
    '''
    
    rad = - m.radians(angle)
    
    ox, oy = origin
    px, py = coord

    qx = ox + m.cos(rad) * (px - ox) - m.sin(rad) * (py - oy)
    qy = oy + m.sin(rad) * (px - ox) + m.cos(rad) * (py - oy)
    
    return qx, qy


#------------------------------------------------------------------------------


def rotate_all_coords(coords,angle,origin=[50,50]):
    '''
    Rotates all 2-D points around some chosen origin in a clock-wise direction.
    '''
    new_coords = []
    for coord in coords:
        new_coord = rotate_coord(coord=coord,angle=angle,origin=origin)
        new_coords.append(list(new_coord))
    return np.array(new_coords)


#------------------------------------------------------------------------------


def get_angle(u:'2D',v:'2D')->'degrees':
    '''
    Returns an angle between 0 and 180 degrees.
    '''
    u = np.array(u)
    v = np.array(v)
    assert u.size == 2
    assert v.size == 2
    _u_ = np.sqrt(np.sum(u**2))
    _v_ = np.sqrt(np.sum(v**2))
    theta = m.acos(np.sum(u*v)/(_u_*_v_))
    return m.degrees(theta)


#------------------------------------------------------------------------------


def get_bearings(start_pt:'2D',end_pt:'2D')->'degrees':
    '''
    Computes a vector (u) from start_pt and end_pt. It then attains the clockwise
    angle between u and the unit vector v = [0,1] that looks North. This is 
    the bearings.
    '''
    start_pt = np.array(start_pt)
    end_pt = np.array(end_pt)
    assert start_pt.size == 2
    assert end_pt.size == 2
    u = end_pt - start_pt
    v = [0,1]  # Unit vector thar faces North. This is zero degrees.
    
    
    # North
    if end_pt[0] == start_pt[0] and end_pt[1] > start_pt[1]:
        bearings = 0
        return bearings
    
    # Q1
    if end_pt[0] > start_pt[0] and end_pt[1] > start_pt[1]:
        theta = get_angle(u,v)
        bearings = theta
        return bearings
    
    # East
    if end_pt[0] > start_pt[0] and end_pt[1] == start_pt[1]:
        bearings = 90
        return bearings
    
    # Q4
    if end_pt[0] > start_pt[0] and end_pt[1] < start_pt[1]:
        theta = get_angle(u,v)
        bearings = theta
        return bearings
    
    # South
    if end_pt[0] == start_pt[0] and end_pt[1] < start_pt[1]:
        bearings = 180
        return bearings
    
    # Q3
    if end_pt[0] < start_pt[0] and end_pt[1] < start_pt[1]:
        theta = get_angle(u,v)
        bearings = 360 - theta
        return bearings
    
    # West
    if end_pt[0] < start_pt[0] and end_pt[1] == start_pt[1]:
        bearings = 270
        return bearings
    
    # Q2
    if end_pt[0] < start_pt[0] and end_pt[1] > start_pt[1]:
        theta = get_angle(u,v)
        bearings = 360 - theta
        return bearings
    
    raise ValueError('No valid cases reached'+\
                     '\nstart_pt: {0}'.format(start_pt)+\
                     '\nend_pt{0}'.format(end_pt))
    
#------------------------------------------------------------------------------
        
    
def cycle_list(list_:list)->'list entry':
    '''
    Modifies original list and return the cycled item,
    '''
    assert isinstance(list_,list)
    item = list_[0]
    del list_[0]
    list_.append(item)
    return item


#------------------------------------------------------------------------------
    
_last_idx = 0

def shuffle_list(list_:list,repeats_allowed=False):
    
    assert isinstance(list_,list)
    
    global _last_idx
    
    N = len(list_)
    
    if repeats_allowed:
        idx = np.random.choice(range(N))
    else:
        idx = np.random.choice(range(N))
        while idx == _last_idx:
            idx = np.random.choice(range(N))
    
    _last_idx = idx
            
    return list_[idx]
    
#------------------------------------------------------------------------------
    

def normalize(array):
    '''
    All number lie between 0 and 1.
    '''
    array = np.array(array)
    MIN = array.min()
    MAX = array.max()
    return (array - MIN)/(MAX-MIN)

#------------------------------------------------------------------------------

def scale255(array):
    '''
    Scales the RGB colors to an integer between 0 and 255.
    This avoids the following Matplotlib warning:
    https://stackoverflow.com/questions/49643907/
    clipping-input-data-to-the-valid-range-for-imshow-with-rgb-data-0-1-for-floa
    '''
    array = normalize(array)
    return np.array(array*255,dtype=np.uint8)

#------------------------------------------------------------------------------


def quarter_circle(center:'2D',radius:'>0',Q='Q1',clockwise=False,N_pts=100):
    
    '''
    Produces coordinates for a quarter circle in (x,y) form.
    '''
    
    center = np.array(center)
    
    e = 1e-6  # to include last point in linspace.
    
    if Q == 'Q1':
        theta = np.linspace(0,np.pi/2+e,N_pts)
    elif Q == 'Q2':
        theta = np.linspace(np.pi/2,np.pi+e,N_pts)
    elif Q == 'Q3':
        theta = np.linspace(np.pi,3*np.pi/2+e,N_pts)
    elif Q == 'Q4':
        theta = np.linspace(3*np.pi/2,2*np.pi+e,N_pts)
    else:
        raise ValueError('Q must be Q1,Q2,Q3 or Q4 and a string.')
    
    x = center[0] + radius*np.cos(theta)
    y = center[1] + radius*np.sin(theta)
    
    if clockwise:
        x = x[::-1]
        y = y[::-1]
        
    return x,y


#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
    
def dist(x1,x2):
    '''
    Computes the distance between two points. Any dimension can be provided.
    '''
    x1 = np.array(x1)
    x2 = np.array(x2)
    return np.sqrt(((x1-x2)**2).sum())
    
#------------------------------------------------------------------------------
    
def orthogonal(vector:'2D'):
    '''
    Returns an orthogonal unit vector.
    '''
    # u1 x v1 + u2 x v2 = 0  (dot product and cos(90) = 0)
    # let v1 = 1
    # v2 = - u1/u2
    v1 = 1
    v2 = -vector[0]/vector[1]
    norm = np.sqrt(v1**2 + v2**2)
    v1 /= norm
    v2 /= norm
    return np.array([v1,v2])  # normalised orthogonal vector


#------------------------------------------------------------------------------


def bearings_to_vector(bearings):
    bearings = bearings 
    rad = m.radians(bearings)
    # Note that sin and cos are switched.
    # This is because bearings start with 0 and the positive y-axis and
    # rotates in the clock-wise direction.
    u1 = m.sin(rad)
    u2 = m.cos(rad)
    norm = np.sqrt(u1**2+u2**2)
    u1 /= norm
    u2 /= norm
    return np.array([u1,u2])

#------------------------------------------------------------------------------


def dict_to_array(dict_:dict):
    '''
    Converts a dictionary of transitions, from N,E,S,W entrances to N,E,S,W
    exits, into a numpy array. 
    An Exception will be raised if:
        1) Self transiions are not zero or None.
        2) Rows do not sum up to one.
    '''
    tpm = np.zeros((4,4))
    idxs = {'N':0,'E':1,'S':2,'W':3}
    keys = list(dict_.keys())
    for key1 in keys:
        idx1 = idxs[key1]
        for key2 in keys:
            idx2 = idxs[key2]
            value = dict_[key1][key2]
            if idx1 == idx2:
                
                if value is None:
                    continue
                if value == 0:
                    continue
                raise ValueError('dict_[{0}][{0}] must have either'+
                                 ' a value of 0 or None.'.format(key1))
            tpm[idx1,idx2] = value
        if tpm[idx1].sum() != 1:
            raise ValueError('Row {0} of dict_ does not sum up to 1.'.format(idx1))
            
    return tpm

#------------------------------------------------------------------------------


def check_tpm(tpm):
    '''
    Takes either a dictionary, list of lists or a numpy array and ensures that
    it meets the following criteria:
        1) All self transition probabiltiies are zero (zero diagonal).
        2) All rows sum up to one (row stochastic).
    '''
    
    if isinstance(tpm,dict):
        return dict_to_array(tpm)
    elif isinstance(tpm,list):
        tpm = np.array(tpm)
        assert np.all(tpm.sum(axis=1)==1)
        assert np.all(np.diag(tpm)==0)
        return tpm
    elif isinstance(tpm,np.ndarray):
        assert np.all(tpm.sum(axis=1)==1)
        assert np.all(np.diag(tpm)==0)
        return tpm
    else:
        raise ValueError('tpm must be a nested dict, list of lists or a '+
                         ' numpy array.')



#------------------------------------------------------------------------------
        
def get_ordered_dict(dictionary:dict):
    return OrderedDict(sorted(dictionary.items()))
            
#------------------------------------------------------------------------------

        
def merge_dicts(*dictionaries,
                 ordered=True,
                 ignore_duplicates=False):
    '''
    Takes several Python dictionaries and merges them into a single 
    dictionary object.
    Keys will be ordered from smallest to largest whether alphabetical 
    or numerical.
    '''
    
    single_dictionary = dict()
    keys = []
    
    for dictionary in dictionaries:
        
        for key in dictionary.keys():
            
            if key in keys:
                message = 'Key {0} has been duplicated! '.format(key)+\
                          'The latest value {0} will be assigned to it'.format(dictionary[key])
                warnings.warn(message)
            else:
                keys.append(key)
                
            single_dictionary[key] = dictionary[key]
            
            
    if ordered:
        return get_ordered_dict(single_dictionary)
        
        
    return single_dictionary 
    
        
#------------------------------------------------------------------------------


def get_pi(P):
    '''
    Get the stationary probability distribution of a discrete Markov Chain.
    '''
    
    M = len(P)
    F = P.T - np.eye(M)
    F[-1] = 1          # last row is all ones
    # solve for pi
    e0 = np.zeros(M)
    e0[-1] = 1  # elementary vector/unit coordinate vector
    pi = np.linalg.solve(F,e0)
    pi = pi.reshape((1,M))             
    return pi[0]

#------------------------------------------------------------------------------








