from typing import Optional, List

from PIL import Image

BACKENDS = {}


def _add_to_backends(class_):
    BACKENDS[class_.get_name()] = class_
    return class_


class OcrWrapper:
    @classmethod
    def get_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def is_available(cls) -> bool:
        raise NotImplementedError

    @classmethod
    def process_image(cls, image: Image, lang: Optional[List[str]] = None) -> str:
        raise NotImplementedError


@_add_to_backends
class OcrWrapperTesseract(OcrWrapper):
    @classmethod
    def get_name(cls) -> str:
        return "tesseract"

    @classmethod
    def is_available(cls) -> bool:
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except ImportError:
            return False
        except EnvironmentError:
            return False

    @classmethod
    def process_image(cls, image: Image, lang: Optional[List[str]] = None) -> str:
        import pytesseract
        lang = "+".join(lang) if lang else None
        result = pytesseract.image_to_string(image, timeout=5, lang=lang).strip()
        if lang and ("chi_sim" in lang or "chi_tra" in lang):
            result = result.replace(" ", "")
        return result


@_add_to_backends
class OcrWrapperCnOcr(OcrWrapper):
    @classmethod
    def get_name(cls) -> str:
        return "cnocr"

    @classmethod
    def is_available(cls) -> bool:
        try:
            import cnocr
            return True
        except ImportError:
            return False

    @classmethod
    def process_image(cls, image: Image, lang: Optional[List[str]] = None) -> str:
        import cnocr
        import numpy as np
        if lang:
            print("Warning: cannot specify language for cnocr")
        ocr = cnocr.CnOcr(model_backend='pytorch')
        image = np.asarray(image.convert('RGB'))
        result = ocr.ocr(image)
        result = "\n".join(map(lambda x: "".join(x[0]), result))
        return result


DEFAULT_BACKEND = OcrWrapperCnOcr
