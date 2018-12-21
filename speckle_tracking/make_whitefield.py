import numpy as np
import scipy.signal

def make_whitefield(data, mask):
    """Estimate the image one would obtain without the sample in the beam.

    This is done by taking the median value at each pixel, then we try 
    to filter bad / zero pixels.

    Parameters
    ----------
    data : ndarray
        Input data, of shape (N, M, L).

    mask : ndarray
        Boolean array of shape (M, L), where True indicates a good
        pixel and False a bad pixel.
    
    Returns
    -------
    W : ndarray
        Float array of shape (M, L) containing the estimated whitefield.
    """
    whitefield = np.median(data, axis=0)
    
    mask2  = mask.copy()
    mask2 *= (whitefield != 0) 

    # fill masked pixels whith neighbouring values
    whitefield[~mask2] = scipy.signal.medfilt(mask2*whitefield, 5)[~mask2]
    whitefield[whitefield==0] = 1.
    return whitefield