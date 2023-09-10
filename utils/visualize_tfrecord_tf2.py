'''
python3 scripts/visualize_tfrecord.py dataset/train.record dataset/labelmap.pbtxt
'''
import matplotlib.pyplot as plt
import numpy as np
import tensorflow.compat.v1 as tf
import sys
import os
import IPython.display
import PIL
import sys

from object_detection.utils import visualization_utils as vu
from object_detection.protos import string_int_label_map_pb2 as pb
from object_detection.data_decoders.tf_example_decoder import TfExampleDecoder as TfDecoder
from google.protobuf import text_format 
import itertools

os.environ["CUDA_VISIBLE_DEVICES"] = "1"
tf.disable_v2_behavior()

tf_record_path = sys.argv[1]
label_map_path = sys.argv[2]

def visualise(tfrecords_filename, label_map=None):
    if label_map is not None:
        label_map_proto = pb.StringIntLabelMap()
        with tf.io.gfile.GFile(label_map,'r') as f:
            text_format.Merge(f.read(), label_map_proto)
            class_dict = {}
            for entry in label_map_proto.item:
                class_dict[entry.id] = {'name':entry.display_name}
    sess = tf.Session()
    decoder = TfDecoder(label_map_proto_file=label_map, use_display_name=False)
    sess.run(tf.tables_initializer())
    topN = itertools.islice(tf.python_io.tf_record_iterator(tfrecords_filename), 5)
    for record in topN:
        example = decoder.decode(record)
        host_example = sess.run(example)
        scores = np.ones(host_example['groundtruth_boxes'].shape[0])
        vu.visualize_boxes_and_labels_on_image_array( 
            host_example['image'],                                               
            host_example['groundtruth_boxes'],                                                     
            host_example['groundtruth_classes'],
            scores,
            class_dict,
            max_boxes_to_draw=None,
            use_normalized_coordinates=True)
        
        im = PIL.Image.fromarray(host_example['image'])
        im.save('vis.jpg')
        
visualise(tf_record_path,label_map_path)
