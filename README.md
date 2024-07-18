# apple-music-artist-albums-checker
获取一个艺术家在Apple Music中所有专辑在全球各地区的存在情况并生成excel文件
## 使用前先安装依赖
pip install requests tqdm pandas openpyxl xlsxwriter
## excel文件预览
https://view.officeapps.live.com/op/view.aspx?src=https://files.catbox.moe/9lgzmt.xlsx
### track_count字段说明
(8)jp表示日区独占且曲目数为8  
(8)ALL表示全区都有且曲目数都为8  
(8)ALL-cn表示除了cn区其他地区都存在且曲目数都为8  
(8)us,(7)cn表示只有us区和cn区有，cn区的曲目数缺少一首
