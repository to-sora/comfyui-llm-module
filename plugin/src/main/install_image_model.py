import hashlib
from .settings import APP
from .ipv4 import enable


def main():
    import httpx
    enable()
    target=APP/'data/image-models/u2netp.onnx'
    if target.exists():
        print('Existing background model retained.')
        return
    url='https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx'
    raw=bytearray()
    with httpx.stream('GET',url,follow_redirects=True,timeout=60) as response:
        response.raise_for_status()
        for chunk in response.iter_bytes():
            raw.extend(chunk)
            if len(raw)>16*1024**2:
                raise ValueError('Unexpected background model download size')
    if hashlib.md5(raw).hexdigest()!='8e83ca70e441ab06c318d82300c84806':
        raise ValueError('Background model checksum mismatch')
    target.parent.mkdir(parents=True,exist_ok=True)
    staging=target.with_suffix('.partial')
    staging.write_bytes(raw)
    staging.replace(target)
    print('Installed U2NetP:',len(raw),'bytes')


if __name__=='__main__':
    main()
