# -*- coding: utf-8 -*-
"""DS-Project2(KFLDA).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13aAG7xy-nnH7mK60sxLRP86YKsnVe0c9
"""

import numpy as np
from sklearn.utils.validation import check_X_y
from sklearn.utils.validation import check_array
from sklearn.metrics.pairwise import pairwise_kernels
from numpy.linalg import inv, det
from scipy.linalg import eigh
# import warnings

class KFDA():
    
    """
    Kernel Fisher Discriminant Analysis (KFDA)
    Discriminant Analysis in high dimensionality using the kernel trick.
    
    Parameters
    ----------
    n_components : int, the amount of Fisher directions to use.
        default=2
        This is limited by the amount of classes minus one.
        Number of components (lower than number of classes -1) for dimensionality reduction.

    kernel : str, ["linear" | "poly" | "rbf" | "sigmoid" | "cosine" | "precomputed"]
        default="linear".
        The kernel to use.
        Use **kwds to pass arguments to these functions.
        See
        https://scikit-learn.org/stable/modules/metrics.html#polynomial-kernel
        for more details.
    
    alpha : float, default=1e-3
        Regularization term for singular within-class matrix.
      
    tol : float, default=1e-4
        Singularity toleration level.

    kprms : mapping of string to any, default=None
        parameters to pass to the kernel function.


    Attributes
    ----------
    X_ : Training vector after applying input validation

    y_ : label vector after applying input validation

    W_ : array of shape (n_components) 
        contains weights of eigen vectors
    
    unique_classes : array of shape (n_classes,)
        The unique class labels
    """
    
    def __init__(self,n_components=2, kernel='linear', alpha=1e-3, tol=1e-4, **kprms):

        self.n_components_ = n_components
        self.kernel_ = kernel
        self.alpha_ = alpha
        self.tol_ = tol
        self.kernel_params_ = kprms
        
        #checking kernel parameter and assinging default value if kernel is None or obj
        if kernel is None or callable(kernel):
            self.kernel_ = 'linear'
    

    def get_kernel_(self, X, Y=None):
        if callable(self.kernel_):
            params = self.kernel_params_ or {}
        else:
            params = self.kernel_params_

        return pairwise_kernels(X, Y, metric=self.kernel_, filter_params=True, **params)

    def fit(self, X,y):
      

      """
        Fit the model from the data in X and the labels in y.
        Parameters
        ----------
        X : array-like, shape (N x d)
            Training vector, where N is the number of samples, and d is the number of features.
        y : array-like, shape (N)
            Labels vector, where N is the number of samples.
        
        Returns
        -------
        self : object
            Returns the instance itself.
      """

      X_, y_ = check_X_y(X,y)
      self.X_, self.y_ = X_, y_
      n, d = X_.shape

      K = self.get_kernel_(X_)

      if self.n_components_ is None:
          ndims = d
      else:
          ndims = self.n_components_

      self.unique_classes, class_counts = np.unique(y, return_counts=True)
      ndims = min(ndims, len(self.unique_classes) - 1)

      # Compute M and N matrices
      M_avg = K.sum(axis=1) / n
      M = np.zeros([n, n])
      N = np.zeros([n, n])
      for i, c in enumerate(self.unique_classes):
          C_i = np.where(y == c)[0]
          K_i = K[:, C_i]
          M_i = K_i.sum(axis=1) / class_counts[i]
          diff = (M_i - M_avg)
          M += class_counts[i] * (diff @ diff.T)
          const_ni = np.full([class_counts[i], class_counts[i]], 1.0 - 1.0 / class_counts[i])
          N += K_i @ const_ni @ K_i.T

      # Regularize matrix N with alpha_
      if abs(det(N)) < self.tol_:
          N += self.alpha_ * np.eye(n)
      
      # Calculate Eigen Values and Vectors
      evals, evecs = eigh(inv(N) @ M)
      evecs = evecs[:, np.argsort(evals)[::-1]]

      # Return Top ndims Eigen Vectors
      self.W_ = evecs[:, :ndims].T
      return self

    def transform(self,X=None):

      """
      Applies the kernel transformation.
        Parameters
        ----------
        X : (N x d) matrix, optional
            Data to transform. If not supplied, the training data will be used.
        Returns
        -------
        transformed: (N x d') matrix.
            Input data transformed by the learned mapping.
      """

      if X is None:
          X = self.X_
      else:
          X = check_array(X, accept_sparse=True)

      # calculate K for X and X~
      K = self.get_kernel_(X,self.X_)
      return K @ self.W_.T



