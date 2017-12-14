import json
import csv
import argparse
import sys
import os


def main(args):
    fp = args['infile']
    geojson_data = json.load(fp)
    if geojson_data['type'] == 'FeatureCollection':
        parse_feature_collection(geojson_data['features'], args['outfile'])
    else:
        print("Can currently only parse FeatureCollections, but I found ", geojson_data['type'], " instead")


def parse_feature_collection(features, outfile):
    # Each feature from the feature collection is a Type: Feature, a bunch of properties, and geometry.
    # We want to flatten those out

    # create the csv writer object
    csvwriter = csv.writer(outfile, lineterminator=os.linesep)

    count = 0
    # We'd like to save the first header we see, to maintain the exact same ordering, in case
    # some features change their order (we can't rely on it!)
    header = []
    for feature in features:
        if count == 0:
            header = list(feature['properties'].keys())
            # We're going to assume the feature is just a point for this stage
            header.extend(['px','py'])
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(feature_to_row(feature, feature['properties'].keys()))
    outfile.close()

def feature_to_row(feature, header):
    l = []
    for k in header:
        l.append(feature['properties'][k])
    if feature['geometry']['type'] != 'Point':
        raise RuntimeError("Expecting point type, but got ", feature['geometry']['type'])
    coords = feature['geometry']['coordinates']
    assert(len(coords)==2)
    l.extend(coords)
    return l


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="geojson2csv.py",
                                     description='Convert simple GeoJSONs to CSVs')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default = sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default = sys.stdout)
    pargs = parser.parse_args()
    main(vars(pargs))
