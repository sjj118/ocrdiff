import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image


def highlight(img1, img2, box1, box2, diff1, diff2):
    img1 = np.array(img1)
    img2 = np.array(img2)
    fig, ax = plt.subplots(1, 2, figsize=(1.05 * (img1.shape[1] + img2.shape[1]) / 100,
                                          max(img1.shape[0], img2.shape[0]) / 100), dpi=100, frameon=False)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    ax[0].imshow(img1)
    ax[1].imshow(img2)
    ax[0].set_axis_off()
    ax[1].set_axis_off()
    for box in box1: ax[0].add_patch(get_rect(box, fill=False, color='green'))
    for box in box2: ax[1].add_patch(get_rect(box, fill=False, color='green'))
    for diff in diff1: ax[0].add_patch(get_rect(diff, fill=True, color='red', alpha=0.4, linewidth=0))
    for diff in diff2: ax[1].add_patch(get_rect(diff, fill=True, color='red', alpha=0.4, linewidth=0))
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    return Image.open(buffer)


def get_rect(box, **kwargs):
    return plt.Rectangle((box.left, box.top), box.width, box.height, **kwargs)
