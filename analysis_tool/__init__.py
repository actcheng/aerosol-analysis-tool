import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.dirname(CURRENT_DIR)+'/analysis_tool')
# sys.path.append('./analysis_tool')
# sys.path.append('./analysis_tool/analysis_tool')

print('Loading analysis_tool')
print(sys.path)
import analysis_utils
from improve_data import ImproveData
from nas_data import NasData
from model_point_data import ModelPointData
from point_avg import PointAvg