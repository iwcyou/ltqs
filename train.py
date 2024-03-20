import torch
import os

from framework import Trainer
from utils.datasets import prepare_Beijing_dataset
from networks.unet import Unet, UnetMoreLayers
from networks.dlinknet import DinkNet34, LinkNet34
from networks.resunet import ResUnet, ResUnet1DConv
from networks.deeplabv3plus import DeepLabV3Plus


def get_model(model_name, use_gps=True):
    input_channels = input_channel_num
    if model_name == 'dlink34':
        model = DinkNet34(num_channels=input_channels)
    elif model_name == 'dlink34_1d':
        model = DinkNet34(num_channels=input_channels, encoder_1dconv=0,
                          decoder_1dconv=4)
    elif model_name == 'linknet':
        model = LinkNet34(num_channels=input_channels,
                          decoder_1dconv=0)
    elif model_name == 'linknet_1d':
        model = LinkNet34(num_channels=input_channels,
                          decoder_1dconv=4)
    elif model_name == 'linknet_nores':
        model = LinkNet34(num_channels=input_channels,
                          decoder_1dconv=0, using_resnet=False)
    elif model_name == 'linknet_nores_1d':
        model = LinkNet34(num_channels=input_channels,
                          decoder_1dconv=4, using_resnet=False)
    elif model_name == 'resunet':
        model = ResUnet(num_channels=input_channels)
    elif model_name == 'resunet_1d':
        model = ResUnet1DConv(num_channels=input_channels)
    elif model_name == 'unet':
        model = Unet(in_channel=input_channels, conv1d=False)
    elif model_name == 'unet_1d':
        model = Unet(in_channel=input_channels, conv1d=True)
    elif model_name == 'unet_more':
        model = UnetMoreLayers(in_channel=input_channels, conv1d=False)
    elif model_name == 'unet_more_1d':
        model = UnetMoreLayers(in_channel=input_channels, conv1d=True)
    elif model_name == 'deeplabv3+':
        model = DeepLabV3Plus(n_classes=1, num_channels=input_channels)
    return model


def get_dataloader(args):
    train_ds, val_ds, test_ds = prepare_Beijing_dataset(args)
    train_dl = torch.utils.data.DataLoader(
        train_ds, batch_size=BATCH_SIZE, num_workers=args.workers, drop_last=True)
    val_dl = torch.utils.data.DataLoader(
        val_ds, batch_size=BATCH_SIZE, num_workers=args.workers, drop_last=True)
    test_dl = torch.utils.data.DataLoader(
        test_ds, batch_size=BATCH_SIZE, num_workers=args.workers, drop_last=True)
    return train_dl, val_dl, test_dl


def train(args):
    net = get_model(args.model, args.gps_dir != '')
    train_dl, val_dl, test_dl = get_dataloader(args)
    optimizer = torch.optim.Adam(params=net.parameters(), lr=args.lr) #优化器
    trainer = Trainer(net, optimizer)
    if args.weight_load_path != '':
        trainer.solver.load_weights(args.weight_load_path)
    trainer.set_train_dl(train_dl)
    trainer.set_validation_dl(val_dl)
    trainer.set_test_dl(test_dl)
    trainer.set_save_path(WEIGHT_SAVE_DIR)

    trainer.fit(epochs=args.epochs)


def sampling_experiment(args):
    from utils.data_loader import ImageGPSDataset
    import numpy as np
    net = get_model(args.model, args.gps_dir != '')
    optimizer = torch.optim.Adam(params=net.parameters(), lr=args.lr)
    trainer = Trainer(net, optimizer)
    if args.weight_load_path != '':
        trainer.solver.load_weights(args.weight_load_path)

    score_list = []
    for sampling_rate in np.arange(0.1, 1.1, 0.1):
        _, _, test_ds = prepare_Beijing_dataset(
            args, aug_sampling_rate=sampling_rate)
        test_dl = torch.utils.data.DataLoader(
            test_ds, batch_size=BATCH_SIZE, num_workers=args.workers)
        _, miou = trainer.fit_one_epoch(test_dl, eval=True)
        print(sampling_rate, miou)
        score_list.append(miou[3].item())

    print(score_list)
    with open(os.path.join(os.path.split(args.weight_load_path)[0], "sampling_experiment.txt"), 'w') as f:
        f.write(str(score_list))
        f.close()


def precision_experiment(args):
    from utils.data_loader import ImageGPSDataset
    import numpy as np
    net = get_model(args.model, args.gps_dir != '')
    optimizer = torch.optim.Adam(params=net.parameters(), lr=args.lr)
    trainer = Trainer(net, optimizer)
    if args.weight_load_path != '':
        trainer.solver.load_weights(args.weight_load_path)

    score_list = []
    for sampling_rate in [0.05] + list(np.arange(0.1, 1.1, 0.1)):
        _, _, test_ds = prepare_Beijing_dataset(
            args, aug_precision_rate=sampling_rate)
        test_dl = torch.utils.data.DataLoader(
            test_ds, batch_size=BATCH_SIZE, num_workers=args.workers)
        _, miou = trainer.fit_one_epoch(test_dl, eval=True)
        print(sampling_rate, miou)
        score_list.append(miou[3].item())

    print(score_list)
    with open(os.path.join(os.path.split(args.weight_load_path)[0], "precision_experiment.txt"), 'w') as f:
        f.write(str(score_list))
        f.close()


# def predict(args):
#     """predict the test dataset and save the result to the predict_dir"""
#     import cv2
#     import numpy as np

#     net = get_model(args.model, args.gps_dir != '')
#     _, _, test_ds = prepare_Beijing_dataset(args)
#     optimizer = torch.optim.Adam(params=net.parameters(), lr=args.lr)
#     trainer = Trainer(net, optimizer)
#     if args.weight_load_path != '':
#         trainer.solver.load_weights(args.weight_load_path)

#     predict_dir = os.path.join(os.path.split(
#         args.weight_load_path)[0], "prediction")
#     if not os.path.exists(predict_dir):
#         os.mkdir(predict_dir)

#     for i, data in enumerate(test_ds):
#         image = data[0]
#         image_id = test_ds.image_list[i]
#         pred = trainer.solver.pred_one_image(image)
#         pred = ((pred) * 255.0).astype(np.uint8)
#         pred_filename = os.path.join(predict_dir, f"{image_id}.png")
#         cv2.imwrite(pred_filename, pred)
#         print("[DONE] predicted image: ", pred_filename)


def predict(args):
    """predict the EMD of test dataset"""
    import cv2
    import numpy as np
    from tqdm import tqdm

    import os
    import re

    # Regular expression pattern to match the epoch number
    pattern = r'epoch(\d+)_'
    # Initialize variables to store the maximum epoch number and corresponding filename
    max_epoch = 0
    max_epoch_filename = ""
    # Iterate through filenames
    for filename in os.listdir(WEIGHT_SAVE_DIR):
        # Check if the filename is not "prediction"
        if filename.endswith(".pth"):
            # Extract epoch number
            match = re.search(pattern, filename)
            if match:
                epoch_number = int(match.group(1))
                # Update max_epoch and max_epoch_filename if the current epoch number is higher
                if epoch_number > max_epoch:
                    max_epoch = epoch_number
                    max_epoch_filename = filename
    # Print the filename with the highest epoch number
    print("Filename with the highest epoch number:", max_epoch_filename)

    net = get_model(args.model, args.gps_dir != '')
    _, _, test_ds = prepare_Beijing_dataset(args)
    optimizer = torch.optim.Adam(params=net.parameters(), lr=args.lr)
    trainer = Trainer(net, optimizer)

    if args.weight_load_path != '':
        trainer.solver.load_weights(args.weight_load_path)
        predict_dir = os.path.join(os.path.split(args.weight_load_path)[0], "prediction")
    else:
        trainer.solver.load_weights(os.path.join(WEIGHT_SAVE_DIR, max_epoch_filename))
        predict_dir = os.path.join(WEIGHT_SAVE_DIR, "prediction")
    if not os.path.exists(predict_dir):
        os.mkdir(predict_dir)

    threshold = 0.5
    sum_distance = 0
    mask_path = "./datasets/dataset_sz_grid/test/mask"
    for i, data in tqdm(enumerate(test_ds)):
        image = data[0]
        image_id = test_ds.image_list[i]
        mask = cv2.imread(os.path.join(mask_path, f"{image_id}_mask.png"), cv2.IMREAD_GRAYSCALE)

        pred, emd = trainer.solver.pred_one_image(image, mask)
        sum_distance += emd

        # save the predicted image
        pred_img = ((pred) * 255.0).astype(np.uint8)
        pred_filename = os.path.join(predict_dir, f"{image_id}.png")
        cv2.imwrite(pred_filename, pred_img)
        # print("[DONE] predicted image: ", pred_filename)

    average_distance = sum_distance / len(os.listdir(mask_path))
    import csv
    # File path to save the CSV file
    csv_file_path = "./emd.csv"
    # Write average_distance to CSV file
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([WEIGHT_SAVE_DIR, average_distance])

    print(f'{WEIGHT_SAVE_DIR}: {average_distance}')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', '-m', type=str, default='dlink34')
    parser.add_argument('--lr', '-lr', type=float, default=2e-4)
    parser.add_argument('--dataset_name', '-n', type=str, default='bj') #数据集名称：bj、sz
    parser.add_argument('--batch_size', '-b', type=int, default=4)
    parser.add_argument('--sat_dir', '-s', type=str,
                        default='datasets/dataset/train_val/image')
    parser.add_argument('--mask_dir', '-M', type=str,
                        default='datasets/dataset/train_val/mask')
    parser.add_argument('--test_sat_dir', type=str,
                        default='datasets/dataset/test/image_test')
    parser.add_argument('--test_mask_dir', type=str,
                        default='datasets/dataset/test/mask')
    parser.add_argument('--gps_dir', '-g', type=str,
                        default='datasets/dataset/GPS/patch')
    parser.add_argument('--gps_type', '-t', type=str, default='data')
    parser.add_argument('--gps_render_type', type=str, default='')
    parser.add_argument('--count_render_type', type=str, default='')
    parser.add_argument('--feature_embedding', '-F', type=str, default='')
    parser.add_argument('--gps_augmentation', '-A', type=str, default='')
    parser.add_argument('--test_gps_augmentation', type=str, default='')
    parser.add_argument('--weight_save_dir', '-W',
                        type=str, default='./weights')
    parser.add_argument('--weight_load_path', '-L', type=str, default='')
    parser.add_argument('--val_size', '-T', type=float, default=0.1)
    parser.add_argument('--use_gpu', '-G', type=bool, default='')
    parser.add_argument('--gpu_ids', '-N', type=str, default='1,2,3')
    parser.add_argument('--workers', '-w', type=int, default=4)
    parser.add_argument('--epochs', '-e', type=int, default=60)
    parser.add_argument('--random_seed', '-r', type=int, default=12345)
    parser.add_argument('--eval', '-E', type=str, default="")
    args = parser.parse_args()

    if args.use_gpu:
        try:
            gpu_list = [int(s) for s in args.gpu_ids.split(',')]
            os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_ids
        except ValueError:
            raise ValueError(
                'Argument --gpu_ids must be a comma-separated list of integers only')
        BATCH_SIZE = args.batch_size * len(gpu_list)
    else:
        BATCH_SIZE = args.batch_size

    if args.sat_dir == "" and args.gps_dir != "" and args.gps_type == "data":
        input_channels = "gpsdata_only"
        input_channel_num = 1
    elif args.sat_dir == "" and args.gps_dir != "" and args.gps_type == "image":
        input_channels = "gpsimage_only"
        input_channel_num = 4
    elif args.sat_dir != "" and args.gps_dir == "":
        input_channels = "sat_only"
        input_channel_num = 3
    elif args.sat_dir != "" and args.gps_dir != "" and args.gps_type == "data":
        input_channels = "sat_gpsdata"
        input_channel_num = 4
    elif args.gps_type == "image":
        input_channels = "sat_gpsimage"
        input_channel_num = 7
    else:
        print("[ERROR] Both input source are empty!")
        exit(1)

    if args.feature_embedding != "":
        num_embedding = args.feature_embedding.split('-')
        input_channel_num += len(num_embedding)
        if "heading" in num_embedding:
            input_channel_num += 1
        print("[INFO] gps embedding: ", num_embedding)

    if not os.path.exists(args.weight_save_dir):
        os.mkdir(args.weight_save_dir)
    WEIGHT_SAVE_DIR = os.path.join(args.weight_save_dir,
                                   f"{args.model}_{input_channels}_{args.gps_render_type}_{args.count_render_type}_{args.feature_embedding}_{args.gps_augmentation}")
    if not os.path.exists(WEIGHT_SAVE_DIR):
        os.mkdir(WEIGHT_SAVE_DIR)

    print("[INFO] input: ", input_channels)
    print("[INFO] channels: ", input_channel_num)

    if args.eval == "":
        train(args)
        print("[DONE] training finished")
    elif args.eval == "sampling_experiment":
        sampling_experiment(args)
        print("[DONE] sampling finished")
    elif args.eval == "precision_experiment":
        precision_experiment(args)
        print("[DONE] precision_experiment finished")
    elif args.eval == "predict":
        predict(args)
        print("[DONE] predict finished")
