import {
  assertFails,
  assertSucceeds,
  initializeTestEnvironment,
} from '@firebase/rules-unit-testing';
import {
  deleteDoc,
  doc,
  getDoc,
  setDoc,
  updateDoc,
} from 'firebase/firestore';
import { readFile } from 'node:fs/promises';

const projectId = 'verite-rules-test';
const testEnvironment = await initializeTestEnvironment({
  projectId,
  firestore: {
    rules: await readFile('infra/firestore.rules', 'utf8'),
    host: '127.0.0.1',
    port: 8085,
  },
});

try {
  const owner = testEnvironment.authenticatedContext('owner').firestore();
  const other = testEnvironment.authenticatedContext('other').firestore();
  const anonymous = testEnvironment.unauthenticatedContext().firestore();
  const project = doc(owner, 'projects/project-1');

  await assertSucceeds(setDoc(project, { owner_id: 'owner', title: 'Owned' }));
  await assertFails(setDoc(doc(other, 'projects/project-2'), { owner_id: 'owner', title: 'Spoofed' }));
  await assertFails(setDoc(doc(anonymous, 'projects/project-3'), { owner_id: 'anonymous', title: 'Anonymous' }));
  await assertSucceeds(getDoc(project));
  await assertFails(getDoc(doc(other, 'projects/project-1')));
  await assertSucceeds(updateDoc(project, { title: 'Updated' }));
  await assertFails(updateDoc(doc(other, 'projects/project-1'), { title: 'Stolen' }));
  await assertFails(updateDoc(project, { owner_id: 'other' }));
  await assertSucceeds(setDoc(doc(owner, 'projects/project-1/scripts/latest/scenes/scene-001'), { scene_number: 1 }));
  await assertFails(setDoc(doc(other, 'projects/project-1/scripts/latest/scenes/scene-002'), { scene_number: 2 }));
  await assertSucceeds(deleteDoc(project));
  console.log('Firestore rules emulator checks passed.');
} finally {
  await testEnvironment.cleanup();
}
