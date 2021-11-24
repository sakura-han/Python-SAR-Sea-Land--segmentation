# Python-SAR-Sea-Land-segmentation-
本项目是使用高精度的海岸线shapefile文件，制作SAR图像的陆地掩膜，在Python上使用osgeo库批量实现SAR图像的海陆分割

用到的海岸线文件是German FOSSGIS小组(https://www.fossgis.de/) 从OSM海岸线中制作了shapefile格式的文件，下载地址为https://osmdata.openstreetmap.de/data/land-polygons.html

 使用QGIS软件打开land-polygons.shp文件
 ![image](https://user-images.githubusercontent.com/71449105/143207446-7a816b0e-8e35-45fd-8978-e42d8ba1ab73.png)
 
 SAR图像海陆分割的实现主要分为3步
 第一步：根据原始SAR图像的tiff文件，提取SAR图像的地理坐标范围，再依据这个坐标范围制作SAR图像的范围掩膜shp文件
 第二步：使用第一步制作好的范围掩膜shp文件，裁剪全球海岸线land-polygons.shp文件，得到SAR图像范围内的陆地掩膜shp文件
 第三步：使用第二步裁剪下来的陆地掩膜文件，用gdal.Warp函数裁剪原始的SAR图像，实现SAR图像的海陆分割
