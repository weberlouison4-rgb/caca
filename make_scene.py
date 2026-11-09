import numpy as np
from PIL import Image
import os, math

OUT = os.path.dirname(os.path.abspath(__file__))

class Mesh:
    def __init__(self):
        self.v = []
        self.f = []
        self.c = []
        self.n = []
        self.g = []
    def add(self, verts, faces, color, name, glow=0.0):
        verts = np.asarray(verts, float)
        base = len(self.v)
        self.v.append(verts)
        for face in faces:
            idx = [base + int(i) for i in face]
            self.f.append(idx)
            self.c.append(color)
            self.n.append(name)
            self.g.append(glow)
    def arrays(self):
        V = np.vstack(self.v)
        F = np.asarray(self.f, dtype=np.int64)
        C = np.asarray(self.c, float)
        G = np.asarray(self.g, float)
        N = np.asarray(self.n, dtype=object)
        return V, F, C, G, N

def sphere(center, radius, color, name, nu=20, nv=14, scale=(1, 1, 1), glow=0.0):
    center = np.asarray(center, float)
    verts = []
    for i in range(nv + 1):
        phi = np.pi * i / nv
        for j in range(nu):
            th = 2 * np.pi * j / nu
            x = np.sin(phi) * np.cos(th)
            y = np.sin(phi) * np.sin(th)
            z = np.cos(phi)
            verts.append([x * scale[0], y * scale[1], z * scale[2]])
    verts = np.asarray(verts) * radius + center
    faces = []
    for i in range(nv):
        for j in range(nu):
            a = i * nu + j
            b = i * nu + (j + 1) % nu
            c = (i + 1) * nu + (j + 1) % nu
            d = (i + 1) * nu + j
            if i == 0:
                faces.append((a, c, d))
            elif i == nv - 1:
                faces.append((a, b, c))
            else:
                faces.append((a, b, c))
                faces.append((a, c, d))
    m = Mesh()
    m.add(verts, faces, color, name, glow)
    return m

def rounded_box(center, size, color, name, nu=22, nv=14, power=5.0, glow=0.0):
    center = np.asarray(center, float)
    a, b, c = size[0] / 2, size[1] / 2, size[2] / 2
    e = 2.0 / power
    def sp(x):
        return np.sign(x) * np.abs(x) ** e
    verts = []
    for i in range(nv + 1):
        phi = -np.pi / 2 + np.pi * i / nv
        for j in range(nu):
            th = 2 * np.pi * j / nu
            x = sp(np.cos(phi) * np.cos(th)) * a
            y = sp(np.cos(phi) * np.sin(th)) * b
            z = sp(np.sin(phi)) * c
            verts.append([x, y, z])
    verts = np.asarray(verts) + center
    faces = []
    for i in range(nv):
        for j in range(nu):
            aI = i * nu + j
            bI = i * nu + (j + 1) % nu
            cI = (i + 1) * nu + (j + 1) % nu
            dI = (i + 1) * nu + j
            if i == 0:
                faces.append((aI, cI, dI))
            elif i == nv - 1:
                faces.append((aI, bI, cI))
            else:
                faces.append((aI, bI, cI))
                faces.append((aI, cI, dI))
    m = Mesh()
    m.add(verts, faces, color, name, glow)
    return m

def box(center, size, color, name, glow=0.0):
    cx, cy, cz = center
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    v = [(cx + dx, cy + dy, cz + dz) for dx in (-sx, sx) for dy in (-sy, sy) for dz in (-sz, sz)]
    # index: i = dx*4 + dy*2 + dz with ordering above
    def I(dx, dy, dz):
        return (0 if dx < 0 else 4) + (0 if dy < 0 else 2) + (0 if dz < 0 else 1)
    faces = [
        (I(-1,-1,-1), I(1,-1,-1), I(1,1,-1), I(-1,1,-1)),
        (I(-1,-1,1), I(-1,1,1), I(1,1,1), I(1,-1,1)),
        (I(-1,-1,-1), I(-1,-1,1), I(1,-1,1), I(1,-1,-1)),
        (I(-1,1,-1), I(1,1,-1), I(1,1,1), I(-1,1,1)),
        (I(-1,-1,-1), I(-1,1,-1), I(-1,1,1), I(-1,-1,1)),
        (I(1,-1,-1), I(1,-1,1), I(1,1,1), I(1,1,-1)),
    ]
    tris = []
    for q in faces:
        tris.append((q[0], q[1], q[2]))
        tris.append((q[0], q[2], q[3]))
    m = Mesh()
    m.add(v, tris, color, name, glow)
    return m

def cylinder(center, radius, height, color, name, n=20, cap=True):
    center = np.asarray(center, float)
    h = height / 2
    verts = []
    for k in (-1, 1):
        for j in range(n):
            th = 2 * np.pi * j / n
            verts.append([radius * np.cos(th), radius * np.sin(th), k * h])
    verts = np.asarray(verts) + center
    faces = []
    for j in range(n):
        j2 = (j + 1) % n
        faces.append((j, j2, n + j2))
        faces.append((j, n + j2, n + j))
        if cap:
            faces.append((j, n + j, j2))
            faces.append((n + j, n + j2, j2))
    m = Mesh()
    m.add(verts, faces, color, name)
    return m

def quad(p1, p2, p3, p4, color, name, glow=0.0):
    m = Mesh()
    m.add([p1, p2, p3, p4], [(0, 1, 2), (0, 2, 3)], color, name, glow)
    return m

def torus_arc(center, R, r, color, name, a0, a1, n=24, m=8):
    center = np.asarray(center, float)
    verts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        for j in range(m):
            b = 2 * np.pi * j / m
            x = (R + r * np.cos(b)) * np.cos(a)
            z = (R + r * np.cos(b)) * np.sin(a)
            y = r * np.sin(b)
            verts.append(center + [x, y, z])
    faces = []
    for i in range(n):
        for j in range(m):
            aI = i * m + j
            bI = i * m + (j + 1) % m
            cI = (i + 1) * m + (j + 1) % m
            dI = (i + 1) * m + j
            faces.append((aI, bI, cI))
            faces.append((aI, cI, dI))
    msh = Mesh()
    msh.add(verts, faces, color, name)
    return msh

def merge(meshes):
    m = Mesh()
    for p in meshes:
        V, F, C, G, N = p.arrays()
        base = len(m.v) and sum(len(x) for x in m.v) or 0
        m.v.append(V)
        for fi, face in enumerate(F):
            m.f.append([base + int(i) for i in face])
            m.c.append(C[fi])
            m.n.append(N[fi])
            m.g.append(G[fi])
    return m

# ---------------- scene ----------------
parts = []

FLOOR = (0.80, 0.70, 0.55)
WALL = (0.90, 0.87, 0.82)
COUCH = (0.83, 0.50, 0.16)
COUCH2 = (0.88, 0.58, 0.24)
POOP = (0.48, 0.30, 0.13)
POOP_D = (0.38, 0.23, 0.10)
WOOD = (0.45, 0.32, 0.20)
DARK = (0.12, 0.12, 0.13)
WHITE = (0.97, 0.97, 0.95)

parts.append(quad((-12, -12, 0), (12, -12, 0), (12, 12, 0), (-12, 12, 0), FLOOR, "floor"))
parts.append(quad((-12, -4.6, 0), (-12, -4.6, 7), (12, -4.6, 7), (12, -4.6, 0), WALL, "wall"))
parts.append(cylinder((0, 0.8, 0.012), 2.6, 0.024, (0.72, 0.38, 0.34), "rug", n=36))

SHADOW = (0.55, 0.50, 0.45)
parts.append(rounded_box((0, 0.5, 0.02), (3.1, 1.6, 0.05), SHADOW, "shadow_couch", power=8.0))
parts.append(rounded_box((0, -3.4, 0.02), (1.9, 0.8, 0.05), SHADOW, "shadow_tv", power=8.0))

for lx in (-1.18, 1.18):
    for ly in (0.05, 0.95):
        parts.append(cylinder((lx, ly, 0.075), 0.055, 0.15, WOOD, "leg", n=12))
parts.append(rounded_box((0, 0.5, 0.45), (2.7, 1.2, 0.6), COUCH, "base"))
parts.append(rounded_box((0, 1.08, 1.0), (2.7, 0.32, 1.1), COUCH, "backrest"))
for sx in (-1.32, 1.32):
    parts.append(rounded_box((sx, 0.5, 0.75), (0.38, 1.2, 0.9), COUCH, "armrest"))
for sx in (-0.62, 0.62):
    parts.append(rounded_box((sx, 0.42, 0.89), (1.18, 1.05, 0.28), COUCH2, "seat_cushion"))
    parts.append(rounded_box((sx, 0.92, 1.05), (1.18, 0.26, 0.8), COUCH2, "back_cushion"))

SEAT_Z = 1.03
parts.append(sphere((0, 0.35, SEAT_Z + 0.02), 0.55, SHADOW, "shadow_poop", scale=(1.0, 0.85, 0.10)))

poop_blobs = [
    ((0.00, 0.35, SEAT_Z + 0.30), 0.42, (1.05, 1.0, 0.72)),
    ((0.04, 0.33, SEAT_Z + 0.68), 0.33, (1.0, 1.0, 0.80)),
    ((-0.03, 0.31, SEAT_Z + 0.98), 0.25, (1.0, 1.0, 0.85)),
    ((0.02, 0.30, SEAT_Z + 1.22), 0.12, (1.0, 1.0, 1.25)),
]
for c, r, s in poop_blobs:
    parts.append(sphere(c, r, POOP, "poop", scale=s, nu=24, nv=18))

eye_z = SEAT_Z + 1.04
for sx in (-0.10, 0.10):
    parts.append(sphere((sx, 0.10, eye_z), 0.078, WHITE, "eye", nu=16, nv=12))
    parts.append(sphere((sx, 0.045, eye_z + 0.005), 0.038, (0.05, 0.04, 0.04), "pupil", nu=12, nv=8))
    parts.append(sphere((sx + 0.012, 0.020, eye_z + 0.022), 0.012, WHITE, "glint", nu=8, nv=6, glow=1.0))
parts.append(torus_arc((0, 0.055, eye_z - 0.09), 0.10, 0.018, POOP_D, "smile", 195, 345))
for sx in (-0.185, 0.185):
    parts.append(sphere((sx, 0.075, eye_z - 0.045), 0.042, (0.85, 0.45, 0.42), "cheek", scale=(1.0, 0.35, 0.7), nu=12, nv=8))

parts.append(box((0.52, 0.32, SEAT_Z + 0.02), (0.09, 0.28, 0.04), (0.15, 0.15, 0.17), "remote"))
parts.append(sphere((0.52, 0.32, SEAT_Z + 0.045), 0.018, (0.8, 0.15, 0.15), "remote_btn", nu=8, nv=6))

parts.append(cylinder((1.32, 0.5, 1.28), 0.15, 0.15, (0.85, 0.22, 0.22), "bowl", n=18))
rng = np.random.default_rng(7)
for k in range(11):
    a = rng.uniform(0, 2 * np.pi)
    rr = rng.uniform(0, 0.10)
    parts.append(sphere((1.32 + rr * np.cos(a), 0.5 + rr * np.sin(a), 1.36 + rng.uniform(0, 0.05)), 0.05, (0.98, 0.94, 0.72), "popcorn", nu=8, nv=6))

TV_Y = -3.4
parts.append(rounded_box((0, TV_Y, 0.35), (1.5, 0.55, 0.7), WOOD, "tv_stand"))
parts.append(box((0, TV_Y, 0.88), (0.3, 0.3, 0.45), DARK, "tv_neck"))
parts.append(rounded_box((0, TV_Y, 1.75), (2.3, 0.14, 1.35), DARK, "tv_frame"))

SY = TV_Y + 0.075
X0, X1 = -1.03, 1.03
ZB, ZT = 1.18, 2.28
sky = [(0.16, 0.25, 0.55), (0.25, 0.38, 0.70), (0.45, 0.52, 0.80), (0.80, 0.60, 0.55), (0.95, 0.72, 0.40), (1.00, 0.85, 0.45)]
nb = len(sky)
for i in range(nb):
    z0 = ZT - (ZT - ZB) * i / nb
    z1 = ZT - (ZT - ZB) * (i + 1) / nb
    parts.append(quad((X0, SY, z1), (X1, SY, z1), (X1, SY, z0), (X0, SY, z0), sky[i], "film", glow=1.0))
sun = [(0.38 + 0.26 * np.cos(2 * np.pi * k / 20), SY, 1.78 + 0.26 * np.sin(2 * np.pi * k / 20)) for k in range(20)]
for k in range(20):
    parts.append(quad(sun[0], sun[k], sun[(k + 1) % 20], (0.38, SY, 1.78), (1.0, 0.88, 0.35), "film_sun", glow=1.0))
parts.append(quad((X0, SY, 1.62), (-0.15, SY, 1.62), (-0.75, SY, ZB), (X0, SY, ZB), (0.12, 0.10, 0.16), "film_mtn", glow=1.0))
parts.append(quad((0.1, SY, 1.75), (0.55, SY, 1.75), (1.05, SY, ZB), (X1, SY, ZB), (0.16, 0.12, 0.20), "film_mtn", glow=1.0))
parts.append(quad((X0, SY, ZB), (X1, SY, ZB), (X1, SY, 1.34), (X0, SY, 1.34), (0.22, 0.45, 0.22), "film_grass", glow=1.0))
parts.append(quad((-0.55, SY, 1.20), (0.55, SY, 1.20), (0.55, SY, 1.28), (-0.55, SY, 1.28), (0.04, 0.04, 0.05), "film_sub", glow=1.0))
for i, (a, b) in enumerate(((-0.42, -0.20), (-0.14, 0.10), (0.18, 0.42))):
    parts.append(quad((a, SY, 1.215), (b, SY, 1.215), (b, SY, 1.265), (a, SY, 1.265), (0.95, 0.95, 0.95), "film_sub_txt", glow=1.0))

scene = merge(parts)
V, F, C, G, N = scene.arrays()
print("vertices:", len(V), "triangles:", len(F))

# ---------------- exporters ----------------
def export_obj(path, V, F, C, N):
    names = []
    for nm in N:
        if nm not in names:
            names.append(nm)
    with open(path + ".obj", "w") as f:
        f.write("# Caca sur le canape, en train de regarder un film\n")
        f.write("mtllib scene.mtl\n")
        for v in V:
            f.write(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}\n")
        for nm in names:
            f.write(f"g {nm}\nusemtl {nm}\n")
            for i, face in enumerate(F):
                if N[i] == nm:
                    f.write("f " + " ".join(str(int(j) + 1) for j in face) + "\n")
    with open(path + ".mtl", "w") as f:
        for nm in names:
            col = C[list(N).index(nm)]
            f.write(f"newmtl {nm}\nKd {col[0]:.4f} {col[1]:.4f} {col[2]:.4f}\nKa {col[0]*0.3:.4f} {col[1]*0.3:.4f} {col[2]*0.3:.4f}\nillum 2\n\n")

def export_stl(path, V, F):
    with open(path, "w") as f:
        f.write("solid caca_scene\n")
        for face in F:
            p = V[face]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            ln = np.linalg.norm(n)
            if ln > 0:
                n = n / ln
            f.write(f"  facet normal {n[0]:.5f} {n[1]:.5f} {n[2]:.5f}\n    outer loop\n")
            for p in V[face]:
                f.write(f"      vertex {p[0]:.5f} {p[1]:.5f} {p[2]:.5f}\n")
            f.write("    endloop\n  endfacet\n")
        f.write("endsolid caca_scene\n")

export_obj(os.path.join(OUT, "scene"), V, F, C, N)
export_stl(os.path.join(OUT, "scene.stl"), V, F)

# ---------------- renderer ----------------
def render(V, F, C, G, eye, target, W=960, H=720, fov=55.0, ss=1.5):
    W2, H2 = int(W * ss), int(H * ss)
    eye = np.asarray(eye, float)
    target = np.asarray(target, float)
    fwd = target - eye
    fwd = fwd / np.linalg.norm(fwd)
    right = np.cross(fwd, (0, 0, 1))
    right = right / np.linalg.norm(right)
    up = np.cross(right, fwd)
    R = np.stack([right, up, -fwd])
    P = (V - eye) @ R.T
    zc = -P[:, 2]
    fpx = (W2 / 2) / math.tan(math.radians(fov) / 2)
    valid = zc > 0.05
    sx = W2 / 2 + fpx * P[:, 0] / np.where(valid, zc, 1)
    sy = H2 / 2 - fpx * P[:, 1] / np.where(valid, zc, 1)
    img = np.zeros((H2, W2, 3))
    t = np.linspace(0, 1, H2)[:, None]
    top = np.array([0.72, 0.82, 0.92])
    bot = np.array([0.93, 0.88, 0.80])
    img[:] = top[None, None, :] * (1 - t[..., None]) + bot[None, None, :] * t[..., None]
    zbuf = np.full((H2, W2), np.inf)
    L = np.asarray([-0.45, -0.5, 0.78])
    L = L / np.linalg.norm(L)
    amb, diff = 0.38, 0.75
    for i, face in enumerate(F):
        if not np.all(valid[face]):
            continue
        p2 = np.stack([sx[face], sy[face]], axis=1)
        z = zc[face]
        minx = max(int(np.floor(p2[:, 0].min())), 0)
        maxx = min(int(np.ceil(p2[:, 0].max())), W2 - 1)
        miny = max(int(np.floor(p2[:, 1].min())), 0)
        maxy = min(int(np.ceil(p2[:, 1].max())), H2 - 1)
        if minx > maxx or miny > maxy:
            continue
        xs = np.arange(minx, maxx + 1)
        ys = np.arange(miny, maxy + 1)
        X, Y = np.meshgrid(xs, ys)
        (x0, y0), (x1, y1), (x2, y2) = p2
        det = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
        if abs(det) < 1e-9:
            continue
        l0 = ((x2 - x1) * (Y - y1) - (y2 - y1) * (X - x1)) / det
        l1 = ((x0 - x2) * (Y - y2) - (y0 - y2) * (X - x2)) / det
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
        if not inside.any():
            continue
        zi = l0 * z[0] + l1 * z[1] + l2 * z[2]
        sub_z = zbuf[miny:maxy + 1, minx:maxx + 1]
        mask = inside & (zi < sub_z)
        if not mask.any():
            continue
        p = V[face]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        ln = np.linalg.norm(n)
        n = n / ln if ln > 0 else n
        centroid = p.mean(axis=0)
        if np.dot(n, eye - centroid) < 0:
            n = -n
        inten = amb + diff * max(0.0, float(np.dot(n, L)))
        inten = max(inten, G[i])
        col = np.clip(C[i] * inten, 0, 1)
        sub_img = img[miny:maxy + 1, minx:maxx + 1]
        sub_img[mask] = col
        sub_z[mask] = zi[mask]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    im = im.resize((W, H), Image.LANCZOS)
    return im

shots = [
    ("preview_epaule", (0.9, 2.9, 3.1), (0, -2.2, 0.8)),
    ("preview_face", (2.4, -2.4, 2.5), (0, 0.3, 1.5)),
    ("preview_ensemble", (5.8, 3.4, 4.2), (0, -1.8, 0.9)),
]
for name, eye, tgt in shots:
    im = render(V, F, C, G, eye, tgt)
    im.save(os.path.join(OUT, name + ".png"))
    print("saved", name)
