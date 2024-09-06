import numpy as np
import requests
from io import BytesIO
from PIL import Image
from sklearn.cluster import KMeans
import time
import matplotlib.pyplot as plt


class ColorExtractor:
    """Analyzes an image and finds a fitting background color."""

    def __init__(self, img, format='RGB', image_processing_size=None):
        """Prepare the image for analysis."""
        if format == 'RGB':
            self.img = img
        elif format == 'BGR':
            self.img = self.img[..., ::-1]
        else:
            raise ValueError('Invalid format. Only RGB and BGR image formats supported.')

        if image_processing_size:
            img = Image.fromarray(self.img)
            self.img = np.asarray(img.resize(image_processing_size, Image.BILINEAR))

    def best_color(self, k=8, color_tol=10, plot=False):
        """Returns a suitable background color for the given image."""
        artwork = self.img.copy()
        self.img = self.img.reshape((self.img.shape[0]*self.img.shape[1], 3))

        clt = KMeans(n_clusters=k)
        clt.fit(self.img)
        hist = self.find_histogram(clt)
        centroids = clt.cluster_centers_

        colorfulness = [self.colorfulness(color[0], color[1], color[2]) for color in centroids]
        max_colorful = np.max(colorfulness)

        if max_colorful < color_tol:
            best_color = [230, 230, 230]  # Default gray if not colorful enough
        else:
            best_color = centroids[np.argmax(colorfulness)]

        if plot:
            bar = np.zeros((50, 300, 3), dtype='uint8')
            square = np.zeros((50, 50, 3), dtype='uint8')
            start_x = 0

            for (percent, color) in zip(hist, centroids):
                end_x = start_x + (percent * 300)
                bar[:, int(start_x):int(end_x)] = color
                start_x = end_x
            square[:] = best_color

            plt.figure()
            plt.subplot(1, 3, 1)
            plt.title('Artwork')
            plt.axis('off')
            plt.imshow(artwork)

            plt.subplot(1, 3, 2)
            plt.title('k = {}'.format(k))
            plt.axis('off')
            plt.imshow(bar)

            plt.subplot(1, 3, 3)
            plt.title('Color {}'.format(square[0][0]))
            plt.axis('off')
            plt.imshow(square)
            plt.tight_layout()

            plt.show(block=False)

        return best_color[0], best_color[1], best_color[2]

    def format_color(self, color):
        """Format the color to be used in CSS."""
        rgb_int = tuple(int(round(c)) for c in color)
        hex_color = '{:02x}{:02x}{:02x}'.format(*rgb_int)
        return hex_color

    def find_histogram(self, clt):
        """Create a histogram of the image."""
        num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        hist, _ = np.histogram(clt.labels_, bins=num_labels)

        hist = hist.astype('float')
        hist /= hist.sum()

        return hist

    def colorfulness(self, r, g, b):
        """Returns a colorfulness index of the given RGB combination."""
        rg = np.absolute(r - g)
        yb = np.absolute(0.5 * (r + g) - b)

        rg_mean, rg_std = (np.mean(rg), np.std(rg))
        yb_mean, yb_std = (np.mean(yb), np.std(yb))

        std_root = np.sqrt((rg_std ** 2) + (yb_std ** 2))
        mean_root = np.sqrt((rg_mean ** 2) + (yb_mean ** 2))

        return std_root + (0.3 * mean_root)


def image_from_url(url, image_processing_size=None):
    """Download an image from a URL and convert it to a NumPy array."""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert('RGB')
    
    if image_processing_size:
        img = img.resize(image_processing_size, Image.BILINEAR)
        
    return np.array(img)