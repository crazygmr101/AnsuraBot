import json
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple

from lib.linq import LINQ


@dataclass
class Recipe:
    result: str


@dataclass
class Item:
    type: str
    name: str

    def __str__(self):
        return self.name.replace("minecraft:", "").replace("_", " ").title() \
            if self.type == "item" \
            else f"Any with tag `{self.name}`"

    def __hash__(self):
        return hash(self.name) * 2 + (1 if self.type == "item" else 0)


@dataclass
class SmeltingRecipe(Recipe):
    ingredient: Item
    experience: float
    cooking_time: int


@dataclass
class SmokingRecipe(SmeltingRecipe):
    pass


@dataclass
class BlastingRecipe(SmeltingRecipe):
    pass


@dataclass
class SmithingRecipe(Recipe):
    base: Item
    addition: Item


@dataclass
class StonecuttingRecipe(Recipe):
    ingredient: Item
    result_count: int


@dataclass
class ShapedCraftingRecipe(Recipe):
    pattern: List[str]
    keys: Dict[str, Item]
    result_count: int


@dataclass
class ShapelessCraftingRecipe(Recipe):
    ingredients: List[Tuple[Item, int]]
    result_count: int


@dataclass
class BlockDrop(Recipe):
    block: Item
    silk: bool
    fortune_chances: List[float]


@dataclass
class ChestLoot(Recipe):
    location: str


@dataclass
class EntityDrop(Recipe):
    entity: str


@dataclass
class Barter(Recipe):
    pass


@dataclass
class CatGift(Recipe):
    pass


@dataclass
class HeroGift(Recipe):
    entity: str


@dataclass
class FishingLoot(Recipe):
    pool: str


@dataclass
class Tag:
    name: str
    items: List[str]


def flatten_loot(js):
    flat = []

    def _fl(item):
        if item["type"] == "minecraft:alternatives":
            for i in item["children"]:
                _fl(i)
        if item["type"] == "minecraft:item":
            for condition in item.get("conditions", []):
                if condition["condition"] == "minecraft:match_tool" and \
                        "enchantments" in condition["predicate"] and \
                        condition["predicate"]["enchantments"][0]["enchantment"] == "minecraft:silk_touch":
                    flat.append([item["name"], True, []])
                    return
                elif condition["condition"] == "minecraft:table_bonus" and \
                        condition["enchantment"] == "minecraft:fortune":
                    flat.append([item["name"], False, condition["chances"]])
                    return
            for function in item.get("functions", []):
                if function.get("enchantment") == "minecraft:fortune":
                    flat.append([item["name"], False, [1]])
                    return
            flat.append([item["name"], False, []])

    for pool in js["pools"]:
        for entry in pool["entries"]:
            _fl(entry)

    return LINQ(flat).distinct_by(lambda x, y: x[0] == y[0]).to_list()


def load_recipes(recipes: List[str]) -> List[Recipe]:
    def resolve_item(item) -> Item:
        if "tag" in item:
            return Item("tag", item["tag"])
        if "item" in item:
            return Item("item", item["item"])

    recipe_list = []
    for fn in recipes:
        with open(fn) as fp:
            content = json.load(fp)
            if content["type"] == "minecraft:crafting_shaped":
                recipe_list.append(ShapedCraftingRecipe(
                    result=content["result"]["item"].replace("minecraft:", ""),
                    pattern=content["pattern"],
                    keys={key: resolve_item(item) for key, item in content["key"].items()},
                    result_count=content["result"].get("count", 1)
                ))
            if content["type"] == "minecraft:stonecutting":
                recipe_list.append(StonecuttingRecipe(
                    result=content["result"].replace("minecraft:", ""),
                    ingredient=resolve_item(content["ingredient"]),
                    result_count=content["count"]
                ))
            if content["type"] == "minecraft:smoking":
                recipe_list.append(SmokingRecipe(
                    result=content["result"].replace("minecraft:", ""),
                    cooking_time=content["cookingtime"],
                    ingredient=resolve_item(content["ingredient"]),
                    experience=content["experience"]
                ))
            if content["type"] == "minecraft:blasting":
                recipe_list.append(BlastingRecipe(
                    result=content["result"].replace("minecraft:", ""),
                    cooking_time=content["cookingtime"],
                    ingredient=resolve_item(content["ingredient"]),
                    experience=content["experience"]
                ))
            if content["type"] == "minecraft:smelting":
                recipe_list.append(SmeltingRecipe(
                    result=content["result"].replace("minecraft:", ""),
                    cooking_time=content["cookingtime"],
                    ingredient=resolve_item(content["ingredient"]),
                    experience=content["experience"]
                ))
            if content["type"] == "minecraft:smithing":
                recipe_list.append(SmithingRecipe(
                    result=content["result"]["item"].replace("minecraft:", ""),
                    addition=resolve_item(content["addition"]),
                    base=resolve_item(content["base"])
                ))
            if content["type"] == "minecraft:crafting_shapeless":
                recipe_list.append(ShapelessCraftingRecipe(
                    result=content["result"]["item"].replace("minecraft:", ""),
                    ingredients=LINQ(content["ingredients"])
                        .select(lambda i: resolve_item(i))  # noqa
                        .counted()
                        .to_list(),
                    result_count=content["result"].get("count", 1)
                ))
            if content["type"] == "minecraft:block":
                if "pools" not in content:
                    continue
                for i in flatten_loot(content):
                    recipe_list.append(BlockDrop(
                        result=i[0].replace("minecraft:", ""),
                        block=Item(type="item", name=fn.split(os.sep)[-1].split(".")[0].replace("_", " ").title()),
                        silk=i[1],
                        fortune_chances=i[2]
                    ))
            if content["type"] == "minecraft:chest":
                if "pools" not in content:
                    continue
                for i in flatten_loot(content):
                    recipe_list.append(ChestLoot(
                        result=i[0].replace("minecraft:", ""),
                        location=fn.split(os.sep)[-1].split(".")[0].replace("_", " ").title()
                    ))
            if content["type"] == "minecraft:entity":
                if "pools" not in content:
                    continue
                for i in flatten_loot(content):
                    recipe_list.append(EntityDrop(
                        result=i[0].replace("minecraft:", ""),
                        entity=fn.split(os.sep)[-1].split(".")[0].replace("_", " ").title()
                    ))
            if content["type"] == "minecraft:barter":
                if "pools" not in content:
                    continue
                for i in flatten_loot(content):
                    recipe_list.append(Barter(
                        result=i[0].replace("minecraft:", "")
                    ))
            if "cat_morning_gift" in fn:
                if "pools" not in content:
                    continue
                for i in flatten_loot(content):
                    recipe_list.append(CatGift(
                        result=i[0].replace("minecraft:", "")
                    ))
            if "hero" in fn:
                if "pools" not in content:
                    continue
                for i in flatten_loot(content):
                    recipe_list.append(HeroGift(
                        result=i[0].replace("minecraft:", ""),
                        entity=fn.split(os.sep)[-1].split(".")[0][:-5].replace("_", " ").title()
                    ))
            if "/fishing/" in fn:
                if "pools" not in content:
                    continue
                for i in flatten_loot(content):
                    recipe_list.append(FishingLoot(
                        result=i[0].replace("minecraft:", ""),
                        pool=fn.split(os.sep)[-1].split(".")[0].title()
                    ))
    return recipe_list


def load_tags(files: List[str]) -> List[Tag]:
    tags = []
    for fn in files:
        with open(fn) as fp:
            tags.append(Tag(
                fn.split(os.sep)[-1].split(".")[0],
                LINQ(json.load(fp)["values"])
                    .select(lambda x: x.replace("minecraft:", ""))  # noqa
                    .to_list()
            ))
    return tags
