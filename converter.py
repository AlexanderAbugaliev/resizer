import os
import glob
import argparse
from simple_settings import LazySettings
from shutil import copyfile
from PIL import Image
from tqdm import tqdm


def parse_args(settings):
    parser = argparse.ArgumentParser(description='Resizer parameters')
    parser.add_argument('--source', action='store', type=str, help='source images folder', required=True)
    parser.add_argument('--result', action='store', type=str, help='folder to store result images', required=True)
    parser.add_argument('--height', action='store', type=int, help='target image height')
    parser.add_argument('--width', action='store', type=int, help='target image width')
    parser.add_argument('--formats', action='store', nargs='+', type=str,
                        help='list of image extensions to convert, separated by space')

    arguments = parser.parse_args()

    if not os.path.isdir(arguments.source):
        raise RuntimeError('"{:s}" is not directory.'.format(arguments.source))
    settings.configure(SOURCE_FOLDER=arguments.source)

    if not os.path.isdir(arguments.result):
        raise RuntimeError('"{:s}" is not directory.'.format(arguments.result))
    if os.listdir(arguments.result):
        raise RuntimeError('"{:s}" directory is not empty.'.format(arguments.result))
    settings.configure(RESULT_FOLDER=arguments.result)

    if arguments.formats is not None:
        for image_format in arguments.formats:
            if image_format not in settings.SUPPORTED_FORMATS:
                raise RuntimeError('Image format "{:s}" is not supported.'.format(image_format))
        settings.configure(CONVERTED_FORMATS=arguments.formats)

    if arguments.height is not None:
        settings.configure(RESULT_HEIGHT=arguments.height)

    if arguments.width is not None:
        settings.configure(RESULT_WIDTH=arguments.width)

    return settings


if __name__ == "__main__":
    settings = LazySettings('settings')
    settings = parse_args(settings)

    search_request = settings.SOURCE_FOLDER + '/**/*.*'
    files_list = glob.glob(search_request, recursive=True)

    result_size = (settings.RESULT_WIDTH, settings.RESULT_HEIGHT)

    for source_path in tqdm(files_list):
        is_convertible = False
        for converted_format in settings.CONVERTED_FORMATS:
            if source_path[-(len(converted_format)+1):] == '.' + converted_format:
                is_convertible = True
                break

        result_path = source_path.replace(settings.SOURCE_FOLDER,
                                          settings.RESULT_FOLDER)

        result_dir = os.path.dirname(result_path)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        if is_convertible:
            target_image = Image.open(source_path)
            result_image = target_image.resize(result_size, Image.LANCZOS)
            result_image.save(result_path)
        else:
            copyfile(source_path, result_path)
