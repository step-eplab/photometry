# photometry
## Запуск
**start.sh** запускает обработку множества ночей, он запускает **startProc.sh** для обработки отдельно каждой ночи, который использует остальные модули *.py:
* **master_calibration_frames.py** создание мастеров калибровочных кадров
* **processing.py** 	обработка изображений
* **createRLCNP.py**	создание начальных кривых блеска отдельно для каждой ночи и для каждой части кадра (Raw Light Curve by Night, Part)

## Переменные
### start.sh
* **dir_raw** путь к директории, в которой лежат папки с изображениями для каждой ночи в формате yy.mm.dd
* **dir_config**	путь к папке с конфигами	
* **dir_res**		путь к папке для результатов
* **catalog_path**	путь к опорному каталогу
* **target**		префикс к названию изображений в папке ноч

* **dir_night** = dir_raw/night	путь к папке с ночью, где night папка с ночью в формате yy.mm.dd
* **dir_data** = в dir_night заменяется dir_raw на dir_res	путь к папке с результатом обработки для ночи
### startProc.sh
Берутся переменные из start.sh
* **dir_night**	=	dir_night/
* **dir_data**	=	dir_data/
* **dir_config**	=	dir_config
* **catalog_path**	=	catalog_path
* **target**		=	target

Вручную в processing.py 
 * **Params_dict, Params_list** конфиги для астрометрии

Вручную в конфиге configs/photo.sex
* **ASSOC_NAME** должен быть указан catalog_path для выбранного поля

