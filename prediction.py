import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from object_detection.utils import label_map_util
import matplotlib.pyplot as plt

from object_detection.utils import visualization_utils as vis_util

class configuration:
    def __init__(self):
        self.model = 'my_model2'
        self.labelmap_path = os.path.join(self.model,'labelmap.pbtxt')
        self.frozen_inference_graph_path = os.path.join(self.model,'frozen_inference_graph.pb')
        self.result = 'static'
        

class predict:
    def __init__(self,input_path):
        self.config = configuration()
        self.input_path = input_path
        self.detection_graph = None
        self.image_np = None
        self.image_np_expanded =None
        self.graph()
        self.load_image_into_numpy_array()
        self.category_index = label_map_util.create_category_index_from_labelmap(self.config.labelmap_path, use_display_name=True)

        
    
    def graph(self):
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.config.frozen_inference_graph_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

    def load_image_into_numpy_array(self):
        image = Image.open(self.input_path)
        image = image.convert('RGB')
        (im_width, im_height) = image.size
        self.image_np= np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
        self.image_np_expanded=np.expand_dims(self.image_np, axis=0)
        

    def run_inference_for_single_image(self):
        with self.detection_graph.as_default():
            with  tf.compat.v1.Session() as sess:
      
                ops = tf.compat.v1.get_default_graph().get_operations()
                all_tensor_names = {output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in ['num_detections', 'detection_boxes', 'detection_scores','detection_classes', 'detection_masks']:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.compat.v1.get_default_graph().get_tensor_by_name(
              tensor_name)
                if 'detection_masks' in tensor_dict:
        
                    detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                    detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
        
                    real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image.shape[0], image.shape[1])
                    detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
        
                    tensor_dict['detection_masks'] = tf.expand_dims( detection_masks_reframed, 0)
                image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name('image_tensor:0')

     
                output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: np.expand_dims(self.image_np, 0)})

     
                output_dict['num_detections'] = int(output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict[
          'detection_classes'][0].astype(np.uint8)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                if 'detection_masks' in output_dict:
                    output_dict['detection_masks'] = output_dict['detection_masks'][0]
        return output_dict

    def print_out(self):
        
        output_dict = self.run_inference_for_single_image( )
  
        vis_util.visualize_boxes_and_labels_on_image_array(
         self.image_np,
      output_dict['detection_boxes'],
      output_dict['detection_classes'],
      output_dict['detection_scores'],
      self.category_index,
      instance_masks=output_dict.get('detection_masks'),
      use_normalized_coordinates=True,
      line_thickness=8)
        
        cv2.imshow("image", self.image_np)
        IMAGE_SIZE = (15,15)
        
        base_name = os.path.basename(self.input_path)
        cv2.imwrite(os.path.join(self.config.result,base_name),self.image_np)
        return os.path.join(self.config.result,base_name)


if __name__ == "__main__":

    input = r'D:\app\images_uploded\Screenshot_7.png'
    predit = predict(input)
    predit.print_out()


