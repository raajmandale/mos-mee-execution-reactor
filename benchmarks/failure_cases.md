# Failure Cases

## Case A
Input:
Unknown highly dissimilar workload

Result:
No reuse selected

Fallback:
Fresh route execution

Status:
Expected behavior

---

## Case B
Weak structural match

Reuse denied.

Fallback route promoted.

---

Conclusion:
System avoids forcing incorrect reuse.