import numpy as np
np.set_printoptions(formatter={'int':hex})
import sys

"""
LidarAnalyzer Class 
Lidar analyzing tools
"""
class LidarDataProcess:

    def __init__(self,N_SEC=8):
        self.N_SEC = N_SEC
        self.offset_av=0
        self.offset_av=0
        self.angle_epsilon=0.05

    # convert compressed array to numpy array of (angle,distance)

    def decompress_data(self,arr_in,check_arr=None):
        arr=np.array(arr_in)

        #angles=arr[:,0] + (arr[:,1] << 8)
        #angles=np.array(angles/100.0)
        dist=np.array(arr[:,0] + (arr[:,1] << 8))
        arr=np.array(dist)
        return arr

    def compress_data(self, offsets):

        #DATA COMPRESSION, see original data size a tuple array of (angle,distance)
        #Conversion trick multiply for 10**N_DEC and remove decimal part
        #get angle and convert to an 8bit integer with 2 decimals
        N_DEC=2
        angles=(np.round(offsets[:,0], N_DEC)*(10**N_DEC)).astype(int)
        distances=np.round(offsets[:,1]).astype(int)

        angles_low=angles & 0x00FF
        angles_hi=(angles & 0xFF00) >> 8
        distances_low=distances & 0x00FF
        distances_hi=(distances & 0xFF00) >> 8
        #split distances in two group of 8 bits


        #print("--------ANGLES--------------")
        #print(angles)

        #print("-----DIST LOW-----------------")
        #print(distances_low)
        #print("-----DIST HI-----------------")
        #print(distances_hi)

        offsets_convert=np.array([distances_low,distances_hi]).T
        #print("---------------offset_convert len={}------------------".format(len(offsets_convert)))
        #print(offsets_convert)
        return offsets_convert


    def decompress_data_angle_and_dist(self,arr_in,check_arr=None):
        arr=np.array(arr_in)

        angles=arr[:,0] + (arr[:,1] << 8)
        angles=np.array(angles/100.0)
        dist=np.array(arr[:,2] + (arr[:,3] << 8))
        arr=np.array([angles,dist]).T
        return arr

    def compress_data_angle_and_dist(self, offsets):
        #DATA COMPRESSION, see original data size a tuple array of (angle,distance)
        #Conversion trick multiply for 10**N_DEC and remove decimal part
        #get angle and convert to an 8bit integer with 2 decimals
        N_DEC=2
        angles=(np.round(offsets[:,0], N_DEC)*(10**N_DEC)).astype(int)
        distances=np.round(offsets[:,1]).astype(int)

        angles_low=angles & 0x00FF
        angles_hi=(angles & 0xFF00) >> 8
        distances_low=distances & 0x00FF
        distances_hi=(distances & 0xFF00) >> 8
        #split distances in two group of 8 bits


        #print("--------ANGLES--------------")
        #print(angles)

        #print("-----DIST LOW-----------------")
        #print(distances_low)
        #print("-----DIST HI-----------------")
        #print(distances_hi)

        offsets_convert=np.array([angles_low,angles_hi,distances_low,distances_hi]).T
        #print("---------------offset_convert len={}------------------".format(len(offsets_convert)))
        #print(offsets_convert)
        return offsets_convert


    def get_scan_vals(self,scan):
        return np.array([(np.radians(meas[1]), meas[2]) for meas in scan]), \
               np.array([meas[0] for meas in scan]), \
               self.feat_extract(scan)
    """
    **split_measures** 
    separate Lidar scan in N_SEC sectors
    """
    def split_measures(self, scan):
        N_SEC=self.N_SEC
        offsets_sects=[]
        intens_sects=[]

        offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
        intens = np.array([meas[0] for meas in scan])

        ang_prec=np.pi / N_SEC
        for i_sec in range(0, N_SEC):
            if i_sec==0:
                ang_start1 = 0
                ang_stop1 = np.pi / N_SEC
                ang_start2 = (2 * N_SEC - 1) * np.pi / N_SEC
                ang_stop2 = 2 * np.pi

                cond=np.where(
                    ((offsets[:,0] > ang_start1) & (offsets[:,0] <= ang_stop1)) |
                    ((offsets[:,0] > ang_start2) & (offsets[:,0] <= ang_stop2)))

            else:
                ang_start = ang_prec
                ang_stop = ang_prec + 2*np.pi/N_SEC

                cond= np.where(
                    ((offsets[:,0] > ang_start) & (offsets[:, 0] <= ang_stop))
                )
                ang_prec = ang_stop

            offsets_sects.append(offsets[cond])
            intens_sects.append(intens[cond])
        return intens_sects,offsets_sects
    """
    **feat_extract**
    get a splitted Lidar scan
    """
    def feat_extract(self,scan):
        #scan_distance = np.array([meas[2] for meas in scan])
        scan_angle = np.array([np.radians(meas[1]) for meas in scan])
        scan_offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
        #scan_intens = np.array([meas[0] for meas in scan])


        angles=np.array([2*i*np.pi/self.N_SEC for i in range(self.N_SEC)])

        #feat lenght is fixed and equal to N_SEC
        feat_dist=np.zeros(self.N_SEC)
        feat = []
        for i_feat in range(0,self.N_SEC):
            if (np.abs(np.asarray(scan_angle) - angles[i_feat])).min() < self.angle_epsilon:
                idx=(np.abs(np.asarray(scan_angle) - angles[i_feat])).argmin()
                #print(np.degrees(scan_angle[idx]),scan_offsets[idx])
                feat_dist[i_feat]=scan_offsets[idx][1]
            feat.append((angles[i_feat], feat_dist[i_feat]))

        return np.array(feat)
