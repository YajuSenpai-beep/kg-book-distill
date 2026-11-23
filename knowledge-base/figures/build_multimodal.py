# -*- coding: utf-8 -*-
"""Build CLIP image/text embeddings for figure/table pages.

Run with the embedding venv:
    .venv-embed\\Scripts\\python.exe figures/build_multimodal.py
Outputs: figures/multimodal_index.npz
"""
import json, os
import numpy as np
from fastembed import ImageEmbedding, TextEmbedding

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
PAGES = json.load(open(os.path.join(BASE, "image-index.json"), encoding="utf-8"))
FIGS = json.load(open(os.path.join(BASE, "figure-index.json"), encoding="utf-8"))


def main():
    img_model = ImageEmbedding(model_name="Qdrant/clip-ViT-B-32-vision",
                               cache_dir=os.path.join(KB, "..", ".embed_cache"))
    txt_model = TextEmbedding(model_name="Qdrant/clip-ViT-B-32-text",
                              cache_dir=os.path.join(KB, "..", ".embed_cache"))
    paths = [os.path.join(KB, p["file"]) for p in PAGES]
    img_vecs = np.array(list(img_model.embed(paths, batch_size=16)), dtype="float32")
    img_vecs /= np.linalg.norm(img_vecs, axis=1, keepdims=True) + 1e-9

    caps = [f"{f['number']} {f['caption']}" for f in FIGS]
    cap_vecs = np.array(list(txt_model.embed(caps, batch_size=32)), dtype="float32")
    cap_vecs /= np.linalg.norm(cap_vecs, axis=1, keepdims=True) + 1e-9

    np.savez(os.path.join(BASE, "multimodal_index.npz"),
             page_vecs=img_vecs,
             page_ids=np.array([f"{p['book']}-{p['page']}" for p in PAGES]),
             page_meta=np.array([json.dumps(p, ensure_ascii=False) for p in PAGES]),
             caption_vecs=cap_vecs,
             caption_ids=np.array([f["id"] for f in FIGS]),
             caption_meta=np.array([json.dumps(f, ensure_ascii=False) for f in FIGS]))
    print("pages", len(PAGES), "captions", len(FIGS))


if __name__ == "__main__":
    main()
