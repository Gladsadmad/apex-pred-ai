import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { after, before, describe, test } from 'node:test';

import {
  editFileTool,
  listFilesTool,
  readFileTool,
  writeFileTool,
} from '../src/tools/file.js';

let dir: string;

before(async () => {
  dir = await mkdtemp(join(tmpdir(), 'apex-file-tools-'));
});

after(() => {
  // mkdtemp lives under the OS temp dir; the OS reaps it
});

const fixture = async (name: string, content: string): Promise<string> => {
  const p = join(dir, name);
  await writeFile(p, content, 'utf-8');
  return p;
};

describe('read_file', () => {
  test('counts lines without a phantom trailing line', async () => {
    const p = await fixture('trailing.txt', 'alpha\nbravo\ncharlie\ndelta\n');
    const out = await readFileTool.execute({ path: p });
    assert.match(out, /of 4/);
    assert.doesNotMatch(out, /\s5\t/);
  });

  test('start_line=0 clamps to the first line instead of wrapping', async () => {
    // slice(-1) used to return the LAST line for start_line=0
    const p = await fixture('zero.txt', 'alpha\nbravo\ncharlie\ndelta');
    const out = await readFileTool.execute({ path: p, start_line: 0 });
    assert.match(out, /alpha/);
    assert.match(out, /delta/);
    assert.match(out, /lines 1-4 of 4/);
  });

  test('negative start_line clamps to the first line', async () => {
    const p = await fixture('neg.txt', 'alpha\nbravo\ncharlie');
    const out = await readFileTool.execute({ path: p, start_line: -5 });
    assert.match(out, /alpha/);
  });

  test('start_line past EOF is an error, not empty output', async () => {
    const p = await fixture('past.txt', 'alpha\nbravo');
    const out = await readFileTool.execute({ path: p, start_line: 99 });
    assert.match(out, /Error/);
  });

  test('end_line past EOF is clamped', async () => {
    const p = await fixture('clamp.txt', 'alpha\nbravo');
    const out = await readFileTool.execute({ path: p, start_line: 1, end_line: 500 });
    assert.match(out, /lines 1-2 of 2/);
  });

  test('honours an explicit range', async () => {
    const p = await fixture('range.txt', 'l1\nl2\nl3\nl4\nl5');
    const out = await readFileTool.execute({ path: p, start_line: 2, end_line: 3 });
    assert.match(out, /l2/);
    assert.match(out, /l3/);
    assert.doesNotMatch(out, /l5/);
  });

  test('reports an empty file as empty', async () => {
    const p = await fixture('empty.txt', '');
    assert.match(await readFileTool.execute({ path: p }), /empty/);
  });

  test('missing file returns an error string', async () => {
    const out = await readFileTool.execute({ path: join(dir, 'nope.txt') });
    assert.match(out, /Error reading file/);
  });
});

describe('edit_file', () => {
  test('inserts $-tokens literally rather than expanding them', async () => {
    // String.replace would expand `$&` to the match and "$`" to the prefix
    const p = await fixture('dollar.txt', 'price: TOKEN end');
    await editFileTool.execute({
      path: p,
      old_string: 'TOKEN',
      new_string: '$& and $` literal',
    });
    assert.equal(await readFile(p, 'utf-8'), 'price: $& and $` literal end');
  });

  test('replace_all also keeps $-tokens literal', async () => {
    const p = await fixture('dollar-all.txt', 'A TOKEN B TOKEN');
    await editFileTool.execute({
      path: p,
      old_string: 'TOKEN',
      new_string: '$$',
      replace_all: true,
    });
    assert.equal(await readFile(p, 'utf-8'), 'A $$ B $$');
  });

  test('replaces only the first occurrence by default', async () => {
    const p = await fixture('single.txt', 'x\ny\nx');
    const out = await editFileTool.execute({ path: p, old_string: 'y', new_string: 'z' });
    assert.match(out, /Replaced 1/);
    assert.equal(await readFile(p, 'utf-8'), 'x\nz\nx');
  });

  test('refuses an ambiguous edit', async () => {
    const p = await fixture('ambiguous.txt', 'dup dup');
    const out = await editFileTool.execute({ path: p, old_string: 'dup', new_string: 'x' });
    assert.match(out, /2 occurrences/);
    assert.equal(await readFile(p, 'utf-8'), 'dup dup');
  });

  test('missing string is an error and leaves the file alone', async () => {
    const p = await fixture('absent.txt', 'hello');
    const out = await editFileTool.execute({ path: p, old_string: 'nope', new_string: 'x' });
    assert.match(out, /not found/);
    assert.equal(await readFile(p, 'utf-8'), 'hello');
  });
});

describe('write_file and list_files', () => {
  test('write_file creates missing parent directories', async () => {
    const p = join(dir, 'nested', 'deep', 'out.txt');
    const out = await writeFileTool.execute({ path: p, content: 'a\nb' });
    assert.match(out, /Written/);
    assert.equal(await readFile(p, 'utf-8'), 'a\nb');
  });

  test('list_files hides dotfiles unless asked', async () => {
    await fixture('.hidden', 'x');
    await fixture('visible.txt', 'x');
    const shown = await listFilesTool.execute({ path: dir });
    assert.match(shown, /visible\.txt/);
    assert.doesNotMatch(shown, /\.hidden/);

    const all = await listFilesTool.execute({ path: dir, include_hidden: true });
    assert.match(all, /\.hidden/);
  });
});
