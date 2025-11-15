import open3d as o3d
import numpy as np
import os

MODEL_PATH = r"C:\Users\Egiso\Downloads\futuristic-car-3d-model\3155-futuristic-car-3d-model\Futuristic Car.obj"
POISSON_DEPTH = 9
VOXEL_SIZE = 0.05
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800

def print_header(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

# STEP 1
def step1_load_and_show(path):
    print_header("STEP 1 — Load Model")
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    mesh = o3d.io.read_triangle_mesh(path)
    if mesh and len(mesh.vertices) > 0:
        if not mesh.has_vertex_normals():
            mesh.compute_vertex_normals()
        print(f"Vertices: {len(mesh.vertices)}, Triangles: {len(mesh.triangles)}, Colors: {mesh.has_vertex_colors()}, Normals: {mesh.has_vertex_normals()}")
        o3d.visualization.draw_geometries([mesh], window_name="Original Mesh",
                                          width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        return mesh, None
    pcd = o3d.io.read_point_cloud(path)
    if pcd and len(pcd.points) > 0:
        print(f"Points: {len(pcd.points)}, Colors: {pcd.has_colors()}")
        o3d.visualization.draw_geometries([pcd], window_name="Original PointCloud",
                                          width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        return None, pcd
    raise RuntimeError("Cannot read file as mesh or point cloud.")

# STEP 2
def step2_mesh_to_pcd(mesh, pcd):
    print_header("STEP 2 — Convert to Point Cloud")
    if mesh:
        pcd_new = mesh.sample_points_uniformly(number_of_points=50000)
    else:
        pcd_new = pcd
    print(f"Points: {len(pcd_new.points)}, Colors: {pcd_new.has_colors()}")
    o3d.visualization.draw_geometries([pcd_new], window_name="Point Cloud",
                                      width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    return pcd_new

# STEP 3
def step3_poisson_reconstruct(pcd):
    print_header("STEP 3 — Poisson Reconstruction")
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=POISSON_DEPTH)
    densities = np.asarray(densities)
    threshold = np.quantile(densities, 0.05)
    mesh.remove_vertices_by_mask(densities <= threshold)
    mesh.compute_vertex_normals()
    print(f"Vertices: {len(mesh.vertices)}, Triangles: {len(mesh.triangles)}, Colors: {mesh.has_vertex_colors()}")
    o3d.visualization.draw_geometries([mesh], window_name="Poisson Mesh",
                                      width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    return mesh

# STEP 4
def step4_voxelize(pcd):
    print_header("STEP 4 — Voxelization")
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=VOXEL_SIZE)
    print(f"Voxels: {len(voxel_grid.get_voxels())}, Colors: {pcd.has_colors()}")
    o3d.visualization.draw_geometries([voxel_grid], window_name="Voxel Grid",
                                      width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    return voxel_grid

# STEP 5 — Большая вертикальная плоскость
def step5_create_large_vertical_plane_mid_object(obj):
    print_header("STEP 5 — Add Extra-Large Vertical Plane at Middle X")
    if isinstance(obj, o3d.geometry.PointCloud):
        pts = np.asarray(obj.points)
    elif isinstance(obj, o3d.geometry.TriangleMesh):
        pts = np.asarray(obj.vertices)
    else:
        raise TypeError("Object must be PointCloud or TriangleMesh")

    # Середина по X
    x_min, x_max = pts[:,0].min(), pts[:,0].max()
    x_mid = (x_min + x_max) / 2.0

    # Размеры плоскости больше объекта по Y и Z
    y_size = (pts[:,1].max() - pts[:,1].min()) * 3.0
    z_size = (pts[:,2].max() - pts[:,2].min()) * 3.0

    # Создаем вертикальную плоскость
    plane = o3d.geometry.TriangleMesh.create_box(width=0.01, height=y_size, depth=z_size)
    plane.translate(-plane.get_center())
    plane.translate((x_mid, 0, 0))

    plane.paint_uniform_color([0.2, 0.2, 0.8])
    plane.compute_vertex_normals()
    o3d.visualization.draw_geometries([obj, plane], window_name="Object + Extra-Large Vertical Plane",
                                      width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    return plane
def clip_pcd_by_plane(pcd, plane_point, plane_normal, keep_positive=False):
    pts = np.asarray(pcd.points)
    mask = np.dot(pts - plane_point, plane_normal) >= 0 if keep_positive else np.dot(pts - plane_point, plane_normal) <= 0
    new_pcd = o3d.geometry.PointCloud()
    new_pcd.points = o3d.utility.Vector3dVector(pts[mask])
    if pcd.has_colors(): new_pcd.colors = o3d.utility.Vector3dVector(np.asarray(pcd.colors)[mask])
    return new_pcd, mask.sum()

def clip_mesh_by_plane(mesh, plane_point, plane_normal, keep_positive=False):
    verts = np.asarray(mesh.vertices)
    tris = np.asarray(mesh.triangles)
    centroids = verts[tris].mean(axis=1)
    keep_tri = tris[np.dot(centroids - plane_point, plane_normal) >= 0 if keep_positive else np.dot(centroids - plane_point, plane_normal) <= 0]
    if len(keep_tri)==0: return o3d.geometry.TriangleMesh(), 0
    unique_vids, new_indices = np.unique(keep_tri.flatten(), return_inverse=True)
    new_mesh = o3d.geometry.TriangleMesh()
    new_mesh.vertices = o3d.utility.Vector3dVector(verts[unique_vids])
    new_mesh.triangles = o3d.utility.Vector3iVector(new_indices.reshape(-1,3))
    if mesh.has_vertex_colors(): new_mesh.vertex_colors = o3d.utility.Vector3dVector(np.asarray(mesh.vertex_colors)[unique_vids])
    if mesh.has_vertex_normals(): new_mesh.vertex_normals = o3d.utility.Vector3dVector(np.asarray(mesh.vertex_normals)[unique_vids])
    return new_mesh, len(new_mesh.vertices) 

# STEP 6 — Обрезка по плоскости
# STEP 6 — Clip object by vertical plane (explicit normal)
def step6_clip_and_show(mesh_or_pcd, plane_mesh):
    print("\n=== STEP 6 — Clip object by vertical plane ===")

    # Мы знаем, что плоскость стоит вертикально по X
    # Нормаль направлена вдоль X
    verts = np.asarray(mesh_or_pcd.points if isinstance(mesh_or_pcd, o3d.geometry.PointCloud) else mesh_or_pcd.vertices)
    x_mid = (verts[:,0].min() + verts[:,0].max()) / 2.0
    plane_point = np.array([x_mid, 0, 0])
    plane_normal = np.array([1.0, 0.0, 0.0])  # нормаль по X

    if isinstance(mesh_or_pcd, o3d.geometry.PointCloud):
        clipped, remaining = clip_pcd_by_plane(mesh_or_pcd, plane_point, plane_normal, keep_positive=False)
        print(f"Points after clipping: {remaining}")
        o3d.visualization.draw_geometries([clipped], window_name="Clipped PointCloud",
                                          width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        return clipped
    
    elif isinstance(mesh_or_pcd, o3d.geometry.TriangleMesh):
        clipped, remaining_vertices = clip_mesh_by_plane(mesh_or_pcd, plane_point, plane_normal, keep_positive=False)
        print(f"Vertices after clipping: {remaining_vertices}, Triangles: {len(clipped.triangles)}")
        o3d.visualization.draw_geometries([clipped], window_name="Clipped Mesh",
                                          width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        return clipped




# STEP 7 — Цвет и экстремумы
def step7_color_and_extremes(obj, axis="z", marker_size=0.03):
    print_header("STEP 7 — Color and Extremes")
    if isinstance(obj, o3d.geometry.PointCloud):
        pts = np.asarray(obj.points)
        colors = np.zeros((len(pts),3))
    elif isinstance(obj, o3d.geometry.TriangleMesh):
        pts = np.asarray(obj.vertices)
        colors = np.zeros((len(pts),3))
    else:
        raise TypeError("Object must be PointCloud or TriangleMesh")

    idx = {"x":0,"y":1,"z":2}[axis.lower()]
    vals = pts[:, idx]
    norm = (vals - vals.min()) / (vals.max() - vals.min() + 1e-9)
    colors[:,0] = norm
    colors[:,1] = 0
    colors[:,2] = 1 - norm

    if isinstance(obj, o3d.geometry.PointCloud):
        obj.colors = o3d.utility.Vector3dVector(colors)
    else:
        obj.vertex_colors = o3d.utility.Vector3dVector(colors)

    min_idx, max_idx = np.argmin(vals), np.argmax(vals)
    min_pt, max_pt = pts[min_idx], pts[max_idx]

    sphere_min = o3d.geometry.TriangleMesh.create_sphere(radius=marker_size)
    sphere_min.paint_uniform_color([0,0,1])
    sphere_min.translate(min_pt)
    sphere_max = o3d.geometry.TriangleMesh.create_sphere(radius=marker_size)
    sphere_max.paint_uniform_color([1,0,0])
    sphere_max.translate(max_pt)

    o3d.visualization.draw_geometries([obj, sphere_min, sphere_max], window_name="Gradient + Extremes",
                                      width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    return min_pt, max_pt

# MAIN
if __name__=="__main__":
    mesh, pcd = step1_load_and_show(MODEL_PATH)
    source_pcd = step2_mesh_to_pcd(mesh, pcd)
    reconstructed_mesh = step3_poisson_reconstruct(source_pcd)
    voxel_grid = step4_voxelize(source_pcd)
    plane_mesh = step5_create_large_vertical_plane_mid_object(source_pcd)  # <-- большая вертикальная плоскость
    clipped_obj = step6_clip_and_show(source_pcd, plane_mesh)
    extrema = step7_color_and_extremes(source_pcd, axis="z")
