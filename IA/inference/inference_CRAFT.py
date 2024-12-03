import argparse
import cv2
import glob
import numpy as np
import os
import torch
import sys
sys.path.append(os.path.abspath('.'))

from basicsr.archs.craft_arch import CRAFT

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='datasets/Set5/LRbicx4', help='input low-resolution image folder')
    parser.add_argument('--output', type=str, default='results/SwinIR/Set5', help='output folder')
    parser.add_argument('--scale', type=int, default=4, help='scale factor: 1, 2, 3, 4, 8')
    parser.add_argument('--model_path', type=str, default='experiments/pretrained_models/CRAFT_MODEL_X4.pth')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Set up model
    model = define_model(args)
    model.eval()
    model = model.to(device)

    window_size = 16

    for idx, path in enumerate(sorted(glob.glob(os.path.join(args.input, '*')))):
        # Read image
        img_lq = cv2.imread(path, cv2.IMREAD_COLOR).astype(np.float32) / 255.
        img_lq = np.transpose(img_lq if img_lq.shape[2] == 1 else img_lq[:, :, [2, 1, 0]], (2, 0, 1))  # HCW-BGR to CHW-RGB
        img_lq = torch.from_numpy(img_lq).float().unsqueeze(0).to(device)  # CHW-RGB to NCHW-RGB

        # Inference
        with torch.no_grad():
            # Pad input image to be a multiple of window_size
            _, _, h_old, w_old = img_lq.size()
            h_pad = (h_old // window_size + 1) * window_size - h_old
            w_pad = (w_old // window_size + 1) * window_size - w_old
            img_lq = torch.cat([img_lq, torch.flip(img_lq, [2])], 2)[:, :, :h_old + h_pad, :]
            img_lq = torch.cat([img_lq, torch.flip(img_lq, [3])], 3)[:, :, :, :w_old + w_pad]

            output = model(img_lq)
            output = output[..., :h_old * args.scale, :w_old * args.scale]

        # Save image
        output = output.data.squeeze().float().cpu().clamp_(0, 1).numpy()
        if output.ndim == 3:
            output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round().astype(np.uint8)
        
        imgname = os.path.splitext(os.path.basename(path))[0]
        cv2.imwrite(os.path.join(args.output, f'{imgname}_CRAFT_x{args.scale}.png'), output)
        
        print(f'Processed image {idx + 1}: {imgname}')

def define_model(args):
    model = CRAFT(
        upscale=args.scale,
        in_chans=3,
        img_size=64,
        window_size=16,
        img_range=1.,
        depths=[2, 2, 2, 2],
        embed_dim=48,
        num_heads=[6, 6, 6, 6],
        mlp_ratio=2,
        resi_connection='1conv')

    loadnet = torch.load(args.model_path, map_location=torch.device('cpu'))
    keyname = 'params_ema' if 'params_ema' in loadnet else 'params'
    model.load_state_dict(loadnet[keyname], strict=True)

    return model

if __name__ == '__main__':
    main()