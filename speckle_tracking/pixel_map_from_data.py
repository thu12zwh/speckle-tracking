import numpy as np
import tqdm

from .make_object_map import make_object_map
from .update_pixel_map import update_pixel_map
from .update_translations import update_translations
from .calc_error import calc_error

# it would be great to generalise this so that 
# no initial estimate of the positions is required

def pixel_map_from_data(data, x, y, W=None, mask=None, u=None):
    """
    solve :
        data[n,i,j] = O[u[0,i,j]-x[n], u[1,i,j]-y[n]]
    
    for u.
    
    Optionally provide W:
        data[n,i,j] = W[i,j] O[u[0,i,j]-x[n], u[1,i,j]-y[n]]
    
    It is assumed that u is irrotational: curl u = 0
    """
    xy    = np.empty((len(x), 2), dtype=np.float)
    xy[:, 0] = x
    xy[:, 1] = y
    shape = data.shape
    
    if mask is None :
        mask = np.ones(shape[1:], dtype=np.bool)
    
    if u is None :
        u = np.array(np.indices(shape[1:]))
    
    if W is None :
        W = np.ones(shape[1:], dtype=np.float64)
    
    # first update O and xy until convergence
    for j in tqdm.trange(10, desc='updating pixel map'):
        
        for i in tqdm.trange(10, desc='updating object map and translations'):
            O, n0, m0 = make_object_map(data, mask, W, xy, u, subpixel=True)
            xy, res   = update_translations(data, mask, W, O, u, n0, m0, xy)
            err_new   = res['error']
            
            if i>0 and (err_old - err_new)/err_old < 1e-3 :
                break
            err_old = err_new
        
        u, res = update_pixel_map(
                    data, mask, W, O, u, n0, m0, xy, 
                    clip = [-40, 40],
                    fill_bad_pix = True, 
                    integrate = True, 
                    quadratic_refinement = True)
        
        uerr_new = res['error'] 
        if j>0 and (uerr_old - uerr_new)/uerr_old < 1e-3 :
            break
        uerr_old = uerr_new
       
    return u, {'object_map': O, 'n0': n0, 'm0': m0, 'pix_positions': xy}