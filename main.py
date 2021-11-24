import osgeo.osr as osr
import os
import numpy as np
from osgeo import gdal
import shapefile      # 使用pyshp

os.environ['PROJ_LIB'] = r'C:\Users\sjtu\.conda\envs\test_torch\Lib\site-packages\osgeo\data\proj'

class Dataset:
    def __init__(self, in_file):
        self.in_file = in_file  # Tiff或者ENVI文件
        self.dataset = gdal.Open(self.in_file)
        self.XSize = self.dataset.RasterXSize  # 网格的X轴像素数量
        self.YSize = self.dataset.RasterYSize  # 网格的Y轴像素数量
        self.GeoTransform = self.dataset.GetGeoTransform()  # 投影转换信息
        self.ProjectionInfo = self.dataset.GetProjection()  # 投影信息
        print(self.GeoTransform)

    def get_lon_lat(self): #获取经纬度信息
        gtf = self.GeoTransform
        coord = []
        left_xy = [gtf[0] - 100, gtf[3] + 100] #[gtf[3], gtf[0]]
        coord.append(left_xy)
        for [x, y] in ([self.XSize + 70, 0], [self.XSize + 70, self.YSize + 70], [0, self.YSize + 70]):
            lat = gtf[0] + x * gtf[1] + y * gtf[2] - 100
            lon = gtf[3] + x * gtf[4] + y * gtf[5] + 100
            coord.append([lat, lon])
        return coord

    def geo2lonlat(self):  #地理坐标转经纬度
        coords = self.get_lon_lat()
        prosrs = osr.SpatialReference()
        prosrs.ImportFromWkt(self.ProjectionInfo) #dataset.GetProjection()
        geosrs = prosrs.CloneGeogCS()
        ct = osr.CoordinateTransformation(prosrs, geosrs)
        L_Lcoords = []
        for coord in coords:
            tmp_coords = ct.TransformPoint(coord[0], coord[1])
            L_Lcoords.append(tmp_coords[:2][::-1])
        return L_Lcoords

    def cut_tiff(self, output_raster, input_shape):
        ds = gdal.Warp(output_raster,
                       self.dataset,
                       format='GTiff',
                       cutlineDSName = input_shape,  # or any other file format
                       # cutlineWhere="FIELD = 'whatever'",
                       # optionally you can filter your cutline (shapefile) based on attribute values
                       # dstNodata=0
                       )  # select the no data value you like
        ds = None

def main(tiff_path):
    dataset = Dataset(tiff_path)       #tiff_path:"E:/new_SAR_data/舰船数据集/1/SARShip-1.0-1/SARShip-1.0-1.tiff"
    coord = dataset.geo2lonlat()  # 获取经纬度信息
    print(coord)

    dir_path = os.path.dirname(tiff_path) #dir_path:"E:/new_SAR_data/舰船数据集/1/SARShip-1.0-1"
    tiff2shp = os.path.join(dir_path, r"cover_shp\rect.shp" ) # 新建数据存放位置
    file = shapefile.Writer(tiff2shp)
    # 创建两个字段
    file.field('FIRST_FLD')
    file.field('type', 'C', '40')
    file.poly([coord])
    file.record('First', 'polygon')

    # 关闭文件操作流
    file.close()
    # 定义投影
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326) # 4326-GCS_WGS_1984; 4490- GCS_China_Geodetic_Coordinate_System_2000
    wkt = proj.ExportToWkt()
    # 写入投影
    f = open(tiff2shp.replace(".shp", ".prj"), 'w')
    f.write(wkt)
    f.close()

    input_shp = r'D:\software_stu\QGIS\land-polygons-complete-4326\land_polygons.shp'  #海陆分割固定
    clip_shp = tiff2shp
    output_shp = os.path.join(dir_path, "cover_shp\output.shp" ) # 新建数据存放位置 r'E:\new_SAR_data\舰船数据集\1\SARShip-1.0-1\cover_shp\output1.shp'

    func_name = "ogr2ogr -clipsrc "
    command = func_name + " " + clip_shp + " " + output_shp + " " + input_shp
    os.system(command)

    if not os.path.exists(os.path.join(dir_path, "output")):
        os.makedirs(os.path.join(dir_path, "output"))
    output_raster = os.path.join(dir_path, "output\output.tiff" ) #r'E:/new_SAR_data/舰船数据集/1/SARShip-1.0-1/output.tiff'   #输出海陆分割后的SAR图像
    dataset.cut_tiff(output_raster, output_shp)

if __name__ == '__main__':
    dataset_path = r'E:\new_SAR_data\舰船数据集\1'
    for dir in os.listdir(dataset_path):
        sub_path = os.path.join(dataset_path, dir)
        if os.path.isdir(sub_path):
            tiff_path = os.path.join(sub_path, dir + '.tiff')
            print(tiff_path)
            main(tiff_path)
