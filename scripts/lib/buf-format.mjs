import fs from 'fs';

const STORAGE = {
  Uint8Array,
  Uint16Array,
  Int16Array,
  Float32Array,
};

export function readBuf(filePath) {
  const buffer = fs.readFileSync(filePath);
  const view = new DataView(buffer.buffer, buffer.byteOffset, buffer.byteLength);
  const jsonLen = view.getUint32(0, true);
  const meta = JSON.parse(buffer.slice(4, 4 + jsonLen).toString('utf8'));
  let offset = 4 + jsonLen;
  const attributes = {};

  for (const attr of meta.attributes) {
    const componentSize = attr.componentSize || 1;
    const count = attr.id === 'indices' ? meta.indexCount : meta.vertexCount;
    const byteLength = count * componentSize * STORAGE[attr.storageType].BYTES_PER_ELEMENT;
    attributes[attr.id] = unpackAttribute(
      attr,
      buffer.slice(offset, offset + byteLength),
      count,
    );
    offset += byteLength;
  }

  return { meta, attributes };
}

export function writeBuf(filePath, meta, attributes) {
  let json = JSON.stringify(meta);
  while ((4 + Buffer.byteLength(json, 'utf8')) % 4 !== 0) {
    json += ' ';
  }
  const jsonBuf = Buffer.from(json, 'utf8');
  const header = Buffer.alloc(4);
  header.writeUInt32LE(jsonBuf.length, 0);
  const chunks = [header, jsonBuf];

  for (const attr of meta.attributes) {
    chunks.push(packAttribute(attr, attributes[attr.id]));
  }

  fs.writeFileSync(filePath, Buffer.concat(chunks));
}

function unpackAttribute(attr, bytes, count) {
  const componentSize = attr.componentSize || 1;
  const TypedArray = STORAGE[attr.storageType];
  const raw = new TypedArray(bytes.buffer, bytes.byteOffset, count * componentSize);

  if (!attr.needsPack) {
    return new Float32Array(raw);
  }

  const packedComponents = attr.packedComponents;
  const out = new Float32Array(count * componentSize);
  const bytesPerElement = TypedArray.BYTES_PER_ELEMENT;
  const isSigned = attr.storageType.indexOf('Int') === 0;
  const max = 1 << (bytesPerElement * 8);
  const bias = isSigned ? max * 0.5 : 0;
  const scale = 1 / max;

  for (let i = 0, t = 0; i < count; i++) {
    for (let c = 0; c < packedComponents.length; c++) {
      const pack = packedComponents[c];
      out[t] = (raw[t] + bias) * scale * pack.delta + pack.from;
      t++;
    }
  }

  return out;
}

function packAttribute(attr, values) {
  const componentSize = attr.componentSize || 1;
  const count = values.length / componentSize;
  const TypedArray = STORAGE[attr.storageType];

  if (!attr.needsPack) {
    const out = new TypedArray(count * componentSize);
    for (let i = 0; i < out.length; i++) {
      out[i] = values[i];
    }
    return Buffer.from(out.buffer, out.byteOffset, out.byteLength);
  }

  const packedComponents = attr.packedComponents;
  const out = new TypedArray(count * componentSize);
  const bytesPerElement = TypedArray.BYTES_PER_ELEMENT;
  const isSigned = attr.storageType.indexOf('Int') === 0;
  const max = 1 << (bytesPerElement * 8);
  const bias = isSigned ? max * 0.5 : 0;
  const scale = 1 / max;
  const maxPacked = max - 1;

  for (let i = 0, t = 0; i < count; i++) {
    for (let c = 0; c < packedComponents.length; c++) {
      const pack = packedComponents[c];
      const normalized = pack.delta === 0 ? 0 : (values[t] - pack.from) / pack.delta;
      let packed = Math.round(normalized / scale - bias);
      packed = Math.max(0, Math.min(maxPacked, packed));
      out[t] = packed;
      t++;
    }
  }

  return Buffer.from(out.buffer, out.byteOffset, out.byteLength);
}

export function buildAttributeMeta(id, values, templateAttr) {
  const componentSize = templateAttr.componentSize || 1;
  const count = values.length / componentSize;

  if (!templateAttr.needsPack) {
    return { ...templateAttr, id };
  }

  const packedComponents = [];
  for (let c = 0; c < componentSize; c++) {
    let min = Infinity;
    let max = -Infinity;
    for (let i = c; i < values.length; i += componentSize) {
      min = Math.min(min, values[i]);
      max = Math.max(max, values[i]);
    }
    if (min === max) {
      max = min + 1e-9;
    }
    packedComponents.push({ from: min, delta: max - min });
  }

  return {
    ...templateAttr,
    id,
    packedComponents,
  };
}

export function geometryToAttributes(geometry, letterValues, centroidValues = null) {
  const position = Float32Array.from(geometry.getAttribute('position').array);
  const normal = Float32Array.from(geometry.getAttribute('normal').array);
  const uv = Float32Array.from(geometry.getAttribute('uv').array);
  const letter = Float32Array.from(letterValues);
  const indices = Float32Array.from(geometry.index.array);

  const attributes = { position, normal, uv, letter, indices };
  if (centroidValues) {
    attributes.centroid = Float32Array.from(centroidValues);
  }
  return attributes;
}
