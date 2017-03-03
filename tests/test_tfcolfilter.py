import os

import pytest
from dtcwt.tf.lowlevel import _HAVE_TF as HAVE_TF
pytest.mark.skipif(not HAVE_TF, reason="Tensorflow not present")

import numpy as np
import tensorflow as tf
from dtcwt.coeffs import biort, qshift
from dtcwt.tf.lowlevel import colfilter
from dtcwt.numpy.lowlevel import colfilter as np_colfilter

import tests.datasets as datasets

def setup():
    global mandrill, mandrill_t
    mandrill = datasets.mandrill()
    mandrill_t = tf.expand_dims(tf.constant(mandrill, dtype=tf.float32),axis=0)

def test_mandrill_loaded():
    assert mandrill.shape == (512, 512)
    assert mandrill.min() >= 0
    assert mandrill.max() <= 1
    assert mandrill.dtype == np.float32
    assert mandrill_t.get_shape() == (1, 512, 512)

def test_odd_size():
    y_op = colfilter(mandrill_t, [-1,2,-1])
    assert y_op.get_shape()[1:] == mandrill.shape

def test_even_size():
    y_op = colfilter(mandrill_t, [-1,-1])
    assert y_op.get_shape()[1:] == (mandrill.shape[0]+1, mandrill.shape[1])

def test_qshift():
    h = qshift('qshift_a')[0]
    y_op = colfilter(mandrill_t, h)
    assert y_op.get_shape()[1:] == (mandrill.shape[0]+1, mandrill.shape[1])

def test_biort():
    h = biort('antonini')[0]
    y_op = colfilter(mandrill_t, h)
    assert y_op.get_shape()[1:] == mandrill.shape

def test_even_size():
    zero_t = tf.zeros([1, *mandrill.shape], tf.float32)
    y_op = colfilter(zero_t, [-1,1])
    assert y_op.get_shape()[1:] == (mandrill.shape[0]+1, mandrill.shape[1])
    with tf.Session() as sess:
        y = sess.run(y_op)
    assert not np.any(y[:] != 0.0)

def test_equal_numpy_biort():
    h = biort('near_sym_b')[0]
    ref = np_colfilter(mandrill, h)
    y_op = colfilter(mandrill_t, h)
    with tf.Session() as sess:
        y = sess.run(y_op)
    np.testing.assert_array_almost_equal(y[0], ref, decimal=4)

def test_equal_numpy_qshift():
    h = qshift('qshift_c')[0]
    ref = np_colfilter(mandrill, h)
    y_op = colfilter(mandrill_t, h)
    with tf.Session() as sess:
        y = sess.run(y_op)
    np.testing.assert_array_almost_equal(y[0], ref, decimal=4)

# vim:sw=4:sts=4:et
