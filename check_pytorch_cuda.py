import torch

print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'CUDA device name: {torch.cuda.get_device_name(0)}')
else:
    print('CUDA version: None')
    print('CUDA device name: None')