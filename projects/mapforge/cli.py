#!/usr/bin/env python3
"""
MapForge CLI - Command-line interface for pixel art map generation

Usage:
    # Generate tileset chain
    python -m mapforge tileset create "ocean" "beach" "grass" --output tilesets/terrain

    # Generate map from tileset
    python -m mapforge map from-tileset tilesets/terrain --width 10 --height 10 --output maps/beach.png

    # Direct map generation
    python -m mapforge map generate "cave with stairs" --width 64 --height 64 --output maps/cave.png

    # Create map object
    python -m mapforge object create "wooden barrel" --width 32 --height 32 --output objects/barrel.png

    # List local tilesets
    python -m mapforge tileset list
"""

import argparse
import sys
from pathlib import Path

from .mapforge import MapForge


def cmd_tileset_create(args):
    """Create a tileset or tileset chain."""
    mf = MapForge()

    terrains = args.terrains

    if len(terrains) < 2:
        print("Error: Need at least 2 terrain descriptions")
        sys.exit(1)

    print(f"\n🎨 Creating tileset chain: {' → '.join(terrains)}")
    print(f"   Tile size: {args.tile_size}px")
    print(f"   Transition: {args.transition}")
    print()

    kwargs = {}
    if args.outline:
        kwargs["outline"] = args.outline
    if args.shading:
        kwargs["shading"] = args.shading
    if args.detail:
        kwargs["detail"] = args.detail

    results = mf.create_tileset_chain(
        terrains,
        transition_size=args.transition,
        tile_size=args.tile_size,
        **kwargs
    )

    print(f"\n✅ Created {len(results)} tileset(s):")
    for result in results:
        print(f"   - {result.tileset_id[:8]} ({result.local_path})")


def cmd_tileset_list(args):
    """List local tilesets."""
    mf = MapForge()

    tilesets = mf.list_tilesets()

    if not tilesets:
        print("No local tilesets found.")
        return

    print(f"\n📁 Local tilesets ({len(tilesets)}):\n")
    for ts in tilesets:
        print(f"   {ts.get('tileset_id', 'unknown')[:8]}")
        print(f"      Path: {ts.get('local_path')}")
        print(f"      Tiles: {ts.get('tile_count', 'unknown')}")
        print()


def cmd_map_from_tileset(args):
    """Generate map from tileset."""
    mf = MapForge()

    tileset_path = Path(args.tileset)
    if not tileset_path.exists():
        # Try assets directory
        tileset_path = mf.assets_dir / "tilesets" / args.tileset
        if not tileset_path.exists():
            print(f"Error: Tileset not found: {args.tileset}")
            sys.exit(1)

    print(f"\n🗺️  Generating map from tileset: {tileset_path.name}")
    print(f"   Size: {args.width}x{args.height} tiles")
    print(f"   Pattern: {args.pattern}")
    print(f"   Scale: {args.scale}x")
    print()

    map_img = mf.generate_map_from_tileset(
        tileset_path,
        width=args.width,
        height=args.height,
        pattern=args.pattern
    )

    output_path = mf.save_map(map_img, args.output, scale=args.scale)
    print(f"\n✅ Map saved: {output_path}")


def cmd_map_generate(args):
    """Generate map region directly."""
    mf = MapForge()

    print(f"\n🎮 Generating map region: {args.description[:50]}...")
    print(f"   Size: {args.width}x{args.height}px")
    print()

    init_image = None
    if args.init_image:
        init_path = Path(args.init_image)
        if init_path.exists():
            init_image = init_path
        else:
            print(f"Warning: Init image not found: {args.init_image}")

    region = mf.generate_region(
        args.description,
        width=args.width,
        height=args.height,
        init_image=init_image
    )

    output_path = mf.save_map(region, args.output, scale=args.scale)
    print(f"\n✅ Region saved: {output_path}")


def cmd_object_create(args):
    """Create a map object."""
    mf = MapForge()

    print(f"\n🎯 Creating object: {args.description[:50]}...")
    print(f"   Size: {args.width}x{args.height}px")
    print()

    region = mf.create_map_object(
        args.description,
        width=args.width,
        height=args.height
    )

    output_path = mf.save_map(region, args.output, scale=args.scale)
    print(f"\n✅ Object saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="mapforge",
        description="MapForge - Pixel art map generation toolkit"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Tileset commands
    tileset_parser = subparsers.add_parser("tileset", help="Tileset operations")
    tileset_sub = tileset_parser.add_subparsers(dest="tileset_cmd")

    # tileset create
    ts_create = tileset_sub.add_parser("create", help="Create tileset chain")
    ts_create.add_argument("terrains", nargs="+", help="Terrain descriptions")
    ts_create.add_argument("--tile-size", type=int, default=16, choices=[16, 32])
    ts_create.add_argument("--transition", type=float, default=0.0)
    ts_create.add_argument("--outline", choices=["single color outline", "selective outline", "lineless"])
    ts_create.add_argument("--shading", choices=["flat shading", "basic shading", "medium shading", "detailed shading", "highly detailed shading"])
    ts_create.add_argument("--detail", choices=["low detail", "medium detail", "highly detailed"])
    ts_create.add_argument("--output", "-o", help="Output directory")
    ts_create.set_defaults(func=cmd_tileset_create)

    # tileset list
    ts_list = tileset_sub.add_parser("list", help="List local tilesets")
    ts_list.set_defaults(func=cmd_tileset_list)

    # Map commands
    map_parser = subparsers.add_parser("map", help="Map operations")
    map_sub = map_parser.add_subparsers(dest="map_cmd")

    # map from-tileset
    map_from_ts = map_sub.add_parser("from-tileset", help="Generate map from tileset")
    map_from_ts.add_argument("tileset", help="Tileset path or ID")
    map_from_ts.add_argument("--width", "-W", type=int, default=10, help="Map width in tiles")
    map_from_ts.add_argument("--height", "-H", type=int, default=10, help="Map height in tiles")
    map_from_ts.add_argument("--pattern", "-p", default="random",
                            choices=["random", "gradient", "checkerboard", "solid_lower", "solid_upper"])
    map_from_ts.add_argument("--scale", "-s", type=int, default=1, help="Scale factor")
    map_from_ts.add_argument("--output", "-o", required=True, help="Output file")
    map_from_ts.set_defaults(func=cmd_map_from_tileset)

    # map generate
    map_gen = map_sub.add_parser("generate", help="Generate map region")
    map_gen.add_argument("description", help="Map description")
    map_gen.add_argument("--width", "-W", type=int, default=64, help="Width in pixels")
    map_gen.add_argument("--height", "-H", type=int, default=64, help="Height in pixels")
    map_gen.add_argument("--init-image", "-i", help="Initial image path")
    map_gen.add_argument("--scale", "-s", type=int, default=1, help="Scale factor")
    map_gen.add_argument("--output", "-o", required=True, help="Output file")
    map_gen.set_defaults(func=cmd_map_generate)

    # Object commands
    obj_parser = subparsers.add_parser("object", help="Object operations")
    obj_sub = obj_parser.add_subparsers(dest="obj_cmd")

    # object create
    obj_create = obj_sub.add_parser("create", help="Create map object")
    obj_create.add_argument("description", help="Object description")
    obj_create.add_argument("--width", "-W", type=int, default=32, help="Width in pixels")
    obj_create.add_argument("--height", "-H", type=int, default=32, help="Height in pixels")
    obj_create.add_argument("--scale", "-s", type=int, default=1, help="Scale factor")
    obj_create.add_argument("--output", "-o", required=True, help="Output file")
    obj_create.set_defaults(func=cmd_object_create)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)
    else:
        # Subcommand not specified
        if args.command == "tileset":
            tileset_parser.print_help()
        elif args.command == "map":
            map_parser.print_help()
        elif args.command == "object":
            obj_parser.print_help()


if __name__ == "__main__":
    main()
