import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("cuda version (wheel):", torch.version.cuda)
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
