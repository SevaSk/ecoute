import torch

print('CUDA available:', torch.cuda.is_available())
print('CUDA device count:', torch.cuda.device_count())
if torch.cuda.is_available():
    print('CUDA version:', torch.version.cuda)
    print('CUDA device name:', torch.cuda.get_device_name(0))
else:
    print('CUDA version: None')
    print('CUDA device name: None')