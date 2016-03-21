'''
(*)~----------------------------------------------------------------------------------
 Pupil - eye tracking platform
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''

import os
import csv
from itertools import chain
import logging
from plugin import Plugin
from pyglui import ui
# logging
logger = logging.getLogger(__name__)



class Raw_Data_Exporter(Plugin):
    '''
    pupil_positions.csv
    keys:
        timestamp - timestamp of the source image frame
        index - associated_frame: closest world video frame
        id - 0 or 1 for left/right eye
        confidence - detector confidence between 0 (not confident) -1 (confident)
        norm_pos_x - x position in the eye image frame in normalized coordinates
        norm_pos_y - y position in the eye image frame in normalized coordinates
        diameter - diameter of the pupil in image pixels as observed in the eye image frame (is not corrected for perspective)

        method - string that indicates what detector was used to detect the pupil

        --- optional fields depending on detector

        #in 2d the pupil appears as an ellipse available in `3d c++` and `2D c++` detector
        2d_ellipse_center_x - x center of the pupil in image pixels
        2d_ellipse_center_y - y center of the pupil in image pixels
        2d_ellipse_axis_a - first axis of the pupil ellipse in pixels
        2d_ellipse_axis_b - second axis of the pupil ellipse in pixels
        2d_ellipse_angle - angle of the ellipse in degrees


        #data made available by the `3d c++` detector

        diameter_3d - diameter of the pupil scaled to mm based on anthropomorphic avg eye ball diameter and corrected for perspective.
        model_confidence - confidence of the current eye model (0-1)
        model_id - id of the current eye model. When a slippage is detected the model is replaced and the id changes.

        sphere_center_x - x pos of the eyeball sphere is eye pinhole camera 3d space units are scaled to mm.
        sphere_center_y - y pos of the eye ball sphere
        sphere_center_z - z pos of the eye ball sphere
        sphere_radius - radius of the eyeball. This is always 12mm (the anthropomorphic avg.) We need to make this assumption because of the `single camera scale ambiguity`.


        circle_3d_center_x - x center of the pupil as 3d circle in eye pinhole camera 3d space units are mm.
        circle_3d_center_y - y center of the pupil as 3d circle
        circle_3d_center_z - z center of the pupil as 3d circle
        circle_3d_normal_x - x normal of the pupil as 3d circle. Indicates the direction that the pupil points at in 3d space.
        circle_3d_normal_y - y normal of the pupil as 3d circle
        circle_3d_normal_z - z normal of the pupil as 3d circle
        circle_3d_radius - radius of the pupil as 3d circle. Same as `diameter_3d`

        theta - circle_3d_normal described in spherical coordinates
        phi - circle_3d_normal described in spherical coordinates

        projected_sphere_center_x - x center of the 3d sphere projected back onto the eye image frame. Units are in image pixels.
        projected_sphere_center_y - y center of the 3d sphere projected back onto the eye image frame
        projected_sphere_axis_a - first axis of the 3d sphere projection.
        projected_sphere_axis_b - second axis of the 3d sphere projection.
        projected_sphere_angle - angle of the 3d sphere projection. Units are degrees.


    gaze_positions.csv
    keys:
        timestamp - timestamp of the source image frame
        index - associated_frame: closest world video frame
        confidence - computed confidence between 0 (not confident) -1 (confident)
        norm_pos_x - x position in the world image frame in normalized coordinates
        norm_pos_y - y position in the world image frame in normalized coordinates
        base - "timestamp-id timestamp-id ..." of pupil data that this gaze position is computed from
    '''
    def __init__(self,g_pool):
        super(Raw_Data_Exporter, self).__init__(g_pool)

    def init_gui(self):
        self.menu = ui.Scrolling_Menu('Raw Data Exporter')
        self.g_pool.gui.append(self.menu)

        def close():
            self.alive = False

        self.menu.append(ui.Button('Close',close))
        self.menu.append(ui.Info_Text('This plugin detects fixations based on a dispersion threshold in terms of degrees of visual angle. It also uses a min duration threshold.'))
        self.menu.append(ui.Info_Text('Select your export frame range using the trim marks in the seek bar. This will affect all exporting plugins.'))
        self.menu.append(ui.Text_Input('in_mark',getter=self.g_pool.trim_marks.get_string,setter=self.g_pool.trim_marks.set_string,label='frame range to export'))

    def deinit_gui(self):
        if self.menu:
            self.g_pool.gui.remove(self.menu)
            self.menu = None


    def on_notify(self,notification):
        if notification['subject'] is "should_export":
            self.export_data(notification['range'],notification['export_dir'])



    def export_data(self,export_range,export_dir):
        with open(os.path.join(export_dir,'pupil_postions.csv'),'wb') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')

            csv_writer.writerow(('timestamp',
                                    'index',
                                    'id',
                                    'confidence',
                                    'norm_pos_x',
                                    'norm_pos_y',
                                    'diameter',
                                    'method',
                                    'ellipse_center_x',
                                    'ellipse_center_y',
                                    'ellipse_axis_a',
                                    'ellipse_axis_b',
                                    'ellipse_angle',
                                    'diameter_3d',
                                    'model_confidence',
                                    'model_id',
                                    'sphere_center_x',
                                    'sphere_center_y',
                                    'sphere_center_z',
                                    'sphere_radius',
                                    'circle_3d_center_x',
                                    'circle_3d_center_y',
                                    'circle_3d_center_z',
                                    'circle_3d_normal_x',
                                    'circle_3d_normal_y',
                                    'circle_3d_normal_z',
                                    'circle_3d_radius',
                                    'theta',
                                    'phi',
                                    'projected_sphere_center_x',
                                    'projected_sphere_center_y',
                                    'projected_sphere_axis_a',
                                    'projected_sphere_axis_b',
                                    'projected_sphere_angle'))

            for p in list(chain(*self.g_pool.pupil_positions_by_frame[export_range])):
                data_2d = [ '%s'%p['timestamp'],  #use str to be consitant with csv lib.
                            p['index'],
                            p['id'],
                            p['confidence'],
                            p['norm_pos'][0],
                            p['norm_pos'][1],
                            p['diameter'],
                            p['method'] ]
                try:
                    ellipse_data = [p['ellipse']['center'][0],
                                    p['ellipse']['center'][1],
                                    p['ellipse']['axes'][0],
                                    p['ellipse']['axes'][1],
                                    p['ellipse']['angle'] ]
                except KeyError:
                    ellipse_data = [None,]*5
                try:
                    data_3d =   [   p['diameter_3d']   ,
                                    p['model_confidence'],
                                    p['model_id'],
                                    p['sphere']['center'][0],
                                    p['sphere']['center'][1],
                                    p['sphere']['center'][2],
                                    p['sphere']['radius'],
                                    p['circle_3d']['center'][0],
                                    p['circle_3d']['center'][1],
                                    p['circle_3d']['center'][2],
                                    p['circle_3d']['normal'][0],
                                    p['circle_3d']['normal'][1],
                                    p['circle_3d']['normal'][2],
                                    p['circle_3d']['radius'],
                                    p['theta'],
                                    p['phi'],
                                    p['projected_sphere']['center'][0],
                                    p['projected_sphere']['center'][1],
                                    p['projected_sphere']['axes'][0],
                                    p['projected_sphere']['axes'][1],
                                    p['projected_sphere']['angle']  ]
                except KeyError as e:
                    data_3d = [None,]*21
                row = data_2d + ellipse_data + data_3d
                csv_writer.writerow(row)
            logger.info("Created 'pupil_positions.csv' file.")

        with open(os.path.join(export_dir,'gaze_postions.csv'),'wb') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(("timestamp",
                                 "index",
                                 "confidence",
                                 "norm_pos_x",
                                 "norm_pos_y",
                                 "base" ) )

            for g in list(chain(*self.g_pool.gaze_positions_by_frame[export_range])):
                data = ['%s'%g["timestamp"],g["index"],g["confidence"],g["norm_pos"][0],g["norm_pos"][1]," ".join(['%s-%s'%(b['timestamp'],b['id']) for b in g['base']]) ] #use str on timestamp to be consitant with csv lib.
                csv_writer.writerow(data)
            logger.info("Created 'gaze_positions.csv' file.")


        with open(os.path.join(export_dir,'pupil_gaze_postions_info.txt'),'w') as info_file:
            info_file.write(self.__doc__)


    def get_init_dict(self):
        return {}

    def cleanup(self):
        self.deinit_gui()
