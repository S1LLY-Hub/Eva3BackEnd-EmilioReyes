-- G07 · Botica Central: datos de ejemplo realistas.
-- Las fechas de vencimiento son relativas a hoy, para que el reporte
-- "vencen en los proximos 30 dias" siempre tenga datos que mostrar y
-- haya un medicamento YA VENCIDO para probar la regla R2.

-- Laboratorios (6)
INSERT INTO laboratorios (nombre, pais) VALUES ('Laboratorio Chile', 'Chile');
INSERT INTO laboratorios (nombre, pais) VALUES ('Recalcine', 'Chile');
INSERT INTO laboratorios (nombre, pais) VALUES ('Saval', 'Chile');
INSERT INTO laboratorios (nombre, pais) VALUES ('Bayer', 'Alemania');
INSERT INTO laboratorios (nombre, pais) VALUES ('Pfizer', 'Estados Unidos');
INSERT INTO laboratorios (nombre, pais) VALUES ('Sanofi', 'Francia');

-- Clientes (5)
INSERT INTO clientes (rut, nombre, email, telefono)
VALUES ('11111111-1', 'Ana Rojas Soto', 'ana.rojas@correo.cl', '+56911111111');
INSERT INTO clientes (rut, nombre, email, telefono)
VALUES ('22222222-2', 'Benjamín Muñoz Díaz', 'benjamin.munoz@correo.cl', '+56922222222');
INSERT INTO clientes (rut, nombre, email, telefono)
VALUES ('33333333-3', 'Camila Pérez Lagos', NULL, NULL);
INSERT INTO clientes (rut, nombre, email, telefono)
VALUES ('44444444-4', 'Diego Fuentes Vera', 'diego.fuentes@correo.cl', '+56944444444');
INSERT INTO clientes (rut, nombre, email, telefono)
VALUES ('55555555-5', 'Elena Castillo Rivas', 'elena.castillo@correo.cl', '+56955555555');

-- Medicamentos (8): 3 con receta, 5 de venta libre.
-- Ids de laboratorio: 1 Lab. Chile, 2 Recalcine, 3 Saval, 4 Bayer, 5 Pfizer, 6 Sanofi
INSERT INTO medicamentos (id_laboratorio, codigo, nombre, descripcion, precio, stock, requiere_receta, fecha_vencimiento)
VALUES (1, 'MED-001', 'Paracetamol 500 mg x 16 comprimidos', 'Analgésico y antipirético', 1990, 120, 0, TRUNC(SYSDATE) + 540);
INSERT INTO medicamentos (id_laboratorio, codigo, nombre, descripcion, precio, stock, requiere_receta, fecha_vencimiento)
VALUES (4, 'MED-002', 'Ibuprofeno 400 mg x 20 comprimidos', 'Antiinflamatorio', 3490, 80, 0, TRUNC(SYSDATE) + 400);
INSERT INTO medicamentos (id_laboratorio, codigo, nombre, descripcion, precio, stock, requiere_receta, fecha_vencimiento)
VALUES (2, 'MED-003', 'Loratadina 10 mg x 10 comprimidos', 'Antialérgico', 2590, 6, 0, TRUNC(SYSDATE) + 20);
INSERT INTO medicamentos (id_laboratorio, codigo, nombre, descripcion, precio, stock, requiere_receta, fecha_vencimiento)
VALUES (3, 'MED-004', 'Omeprazol 20 mg x 14 cápsulas', 'Protector gástrico', 4290, 45, 0, TRUNC(SYSDATE) + 25);
INSERT INTO medicamentos (id_laboratorio, codigo, nombre, descripcion, precio, stock, requiere_receta, fecha_vencimiento)
VALUES (6, 'MED-005', 'Jarabe para la tos 120 ml', 'Antitusivo', 3190, 30, 0, TRUNC(SYSDATE) - 15);
INSERT INTO medicamentos (id_laboratorio, codigo, nombre, descripcion, precio, stock, requiere_receta, fecha_vencimiento)
VALUES (5, 'MED-101', 'Amoxicilina 500 mg x 21 cápsulas', 'Antibiótico. Requiere receta médica', 5990, 40, 1, TRUNC(SYSDATE) + 300);
INSERT INTO medicamentos (id_laboratorio, codigo, nombre, descripcion, precio, stock, requiere_receta, fecha_vencimiento)
VALUES (3, 'MED-102', 'Losartán 50 mg x 30 comprimidos', 'Antihipertensivo. Requiere receta médica', 6490, 3, 1, TRUNC(SYSDATE) + 28);
INSERT INTO medicamentos (id_laboratorio, codigo, nombre, descripcion, precio, stock, requiere_receta, fecha_vencimiento)
VALUES (2, 'MED-103', 'Clonazepam 2 mg x 30 comprimidos', 'Ansiolítico. Requiere receta retenida', 7990, 0, 1, TRUNC(SYSDATE) + 200);

COMMIT;