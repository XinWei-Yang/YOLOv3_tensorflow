from utils import extract_labels
import tensorflow as tf
import numpy as np
import cv2

def create_placeholder( inputs, labels ):
    X = tf.placeholder( tf.float32, [None, input.shape[1], input.shape[2], 3] )
    Y = tf.placeholder( tf.float32, [None, labels.shape[1], labels.shape[2], 3] )

    return X, Y


def Leaky_Relu( input, alpha = 0.01 ):
    output = tf.maximum( input, tf.multiply( input, alpha ) )

    return output


def conv2d( inputs, filters, shape, stride = ( 1, 1 ) ):
    layer = tf.layers.conv2d( inputs,
                              filters,
                              shape,
                              stride,
                              padding = 'SAME',
                              kernel_initializer=tf.truncated_normal_initializer(stddev=0.01) )

    layer = tf.layers.batch_normalization( layer )

    layer = Leaky_Relu( layer )

    return layer


def Res_conv2d( inputs, filters, shape, stride = ( 1, 1 ) ):
    layer = tf.layers.conv2d( inputs,
                              filters,
                              shape,
                              stride,
                              padding = 'SAME',
                              kernel_initializer = tf.truncated_normal_initializer( stddev = 0.01 ) )

    layer = tf.layers.batch_normalization( layer )

    return layer

def Res( input, shortcut ):

    layer = Leaky_Relu( tf.add( input, shortcut ) )

    return layer




def net( inputs ):
    layer = conv2d( inputs, 32, [3, 3] )
    layer = conv2d( layer, 64, [3, 3], ( 2, 2 ) )
    shortcut = layer

    layer = conv2d( layer, 32, [1, 1] )
    layer = Res_conv2d( layer, 64, [3, 3] )
    layer = Res( layer, shortcut )

    layer = conv2d( layer, 128, [3, 3], ( 2, 2 ) )
    shortcut = layer

    for _ in range( 2 ):
        layer = conv2d( layer, 64, [1, 1] )
        layer = Res_conv2d( layer, 128, [3, 3] )
        layer = Res( layer, shortcut )

    layer = conv2d( layer, 256, [3, 3], ( 2, 2 ) )
    shortcut = layer

    for _ in range( 8 ):
        layer = conv2d( layer, 128, [1, 1] )
        layer = Res_conv2d( layer, 256, [3, 3] )
        layer = Res( layer, shortcut )

    layer = conv2d( layer, 512, [3, 3], ( 2, 2 ) )
    shortcut = layer

    for _ in range( 8 ):
        layer = conv2d( layer, 256, [1, 1] )
        layer = Res_conv2d( layer, 512, [3, 3] )
        layer = Res( layer, shortcut )

    layer = conv2d( layer, 1024, [3, 3], ( 2, 2 ) )
    shortcut = layer

    for _ in range( 4 ):
        layer = conv2d( layer, 512, [1, 1] )
        layer = Res_conv2d( layer, 1024, [3, 3] )
        layer = Res( layer, shortcut )

    avg_pool = tf.nn.pool( layer, 'AVG', 'SAME' )
    fc = tf.layers.dense( avg_pool, 1000 )
    softmax = tf.nn.softmax( fc )

    return layer,  softmax

'''--------Test the net--------'''
if __name__ == "__main__":
    data = cv2.imread(  '../data/VOCtest_06-Nov-2007/JPEGImages/000001.jpg' )
    data = cv2.cvtColor( data, cv2.COLOR_BGR2RGB )

    data = tf.cast( tf.expand_dims( tf.constant( data ), 0 ), tf.float32 )

    layer, softmax = net(data)

    with tf.Session() as sess:

        sess.run( tf.initialize_all_variables() )

        print( sess.run( softmax ).shape )

