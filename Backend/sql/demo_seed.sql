-- WOOKNOON Banking Refund System
-- Demo seed data for the current Prisma schema.
-- WARNING: This clears existing data in the demo database.
-- Demo password for all seeded users: Demo@12345

BEGIN;

TRUNCATE TABLE
  "AuditLog",
  "IdempotencyKey",
  "Refund",
  "Transaction",
  "User"
RESTART IDENTITY CASCADE;

-- ============================================================
-- USERS
-- ============================================================
INSERT INTO "User" ("id", "email", "name", "passwordHash", "role", "createdAt") VALUES
('10000000-0000-4000-8000-000000000001', 'amara.okafor@example.com', 'Amara Okafor', '$argon2id$v=19$m=65536,t=3,p=4$Uckt+c4jUgQoELLey/nb3Q$AiRmi9KhB8vhdKD8VDrg4nist+BnITKzabPaOTON/Xc', 'CUSTOMER', '2026-08-01T09:00:00Z'),
('10000000-0000-4000-8000-000000000002', 'daniel.ade@example.com', 'Daniel Adeyemi', '$argon2id$v=19$m=65536,t=3,p=4$Uckt+c4jUgQoELLey/nb3Q$AiRmi9KhB8vhdKD8VDrg4nist+BnITKzabPaOTON/Xc', 'CUSTOMER', '2026-08-03T10:15:00Z'),
('10000000-0000-4000-8000-000000000003', 'fatima.bello@example.com', 'Fatima Bello', '$argon2id$v=19$m=65536,t=3,p=4$Uckt+c4jUgQoELLey/nb3Q$AiRmi9KhB8vhdKD8VDrg4nist+BnITKzabPaOTON/Xc', 'CUSTOMER', '2026-08-05T12:30:00Z'),
('10000000-0000-4000-8000-000000000004', 'developer@wooknoon.demo', 'System Developer', '$argon2id$v=19$m=65536,t=3,p=4$Uckt+c4jUgQoELLey/nb3Q$AiRmi9KhB8vhdKD8VDrg4nist+BnITKzabPaOTON/Xc', 'DEVELOPER', '2026-07-15T08:00:00Z'),
('10000000-0000-4000-8000-000000000005', 'admin@wooknoon.demo', 'System Administrator', '$argon2id$v=19$m=65536,t=3,p=4$Uckt+c4jUgQoELLey/nb3Q$AiRmi9KhB8vhdKD8VDrg4nist+BnITKzabPaOTON/Xc', 'ADMIN', '2026-07-10T08:00:00Z'),
('10000000-0000-4000-8000-000000000006', 'grace.obi@example.com', 'Grace Obi', '$argon2id$v=19$m=65536,t=3,p=4$Uckt+c4jUgQoELLey/nb3Q$AiRmi9KhB8vhdKD8VDrg4nist+BnITKzabPaOTON/Xc', 'CUSTOMER', '2026-08-09T14:00:00Z');

-- ============================================================
-- 15 TRANSACTIONS
-- Covers PENDING, COMPLETED, FAILED and REVERSED.
-- Includes refunded and non-refunded transactions.
-- ============================================================
INSERT INTO "Transaction"
("id", "orderId", "userId", "accountName", "amount", "currency", "status", "description", "finalSale", "createdAt", "refunded") VALUES
('20000000-0000-4000-8000-000000000001', 'ORD-10001', '10000000-0000-4000-8000-000000000001', 'Amara Okafor', 125.50, 'USD', 'COMPLETED', 'Online grocery payment', false, '2026-09-01T10:20:00Z', false),
('20000000-0000-4000-8000-000000000002', 'ORD-10002', '10000000-0000-4000-8000-000000000001', 'Amara Okafor', 75.00, 'USD', 'COMPLETED', 'Duplicate subscription charge', false, '2026-09-02T11:10:00Z', true),
('20000000-0000-4000-8000-000000000003', 'ORD-10003', '10000000-0000-4000-8000-000000000001', 'Amara Okafor', 310.00, 'USD', 'PENDING', 'Electronics purchase awaiting settlement', false, '2026-09-03T13:05:00Z', false),
('20000000-0000-4000-8000-000000000004', 'ORD-10004', '10000000-0000-4000-8000-000000000002', 'Daniel Adeyemi', 49.99, 'USD', 'FAILED', 'Payment failed at merchant', false, '2026-09-04T09:40:00Z', false),
('20000000-0000-4000-8000-000000000005', 'ORD-10005', '10000000-0000-4000-8000-000000000002', 'Daniel Adeyemi', 220.00, 'USD', 'REVERSED', 'Reversed card payment', false, '2026-09-04T16:15:00Z', false),
('20000000-0000-4000-8000-000000000006', 'ORD-10006', '10000000-0000-4000-8000-000000000002', 'Daniel Adeyemi', 850.00, 'USD', 'COMPLETED', 'Laptop purchase', false, '2026-09-05T12:45:00Z', false),
('20000000-0000-4000-8000-000000000007', 'ORD-10007', '10000000-0000-4000-8000-000000000003', 'Fatima Bello', 35.75, 'USD', 'COMPLETED', 'Food delivery', false, '2026-09-06T18:20:00Z', true),
('20000000-0000-4000-8000-000000000008', 'ORD-10008', '10000000-0000-4000-8000-000000000003', 'Fatima Bello', 1200.00, 'USD', 'COMPLETED', 'International tuition payment', false, '2026-09-07T08:30:00Z', false),
('20000000-0000-4000-8000-000000000009', 'ORD-10009', '10000000-0000-4000-8000-000000000003', 'Fatima Bello', 410.25, 'USD', 'PENDING', 'Travel reservation', false, '2026-09-08T15:50:00Z', false),
('20000000-0000-4000-8000-000000000010', 'ORD-10010', '10000000-0000-4000-8000-000000000006', 'Grace Obi', 99.00, 'USD', 'COMPLETED', 'Annual software subscription', false, '2026-09-09T10:05:00Z', false),
('20000000-0000-4000-8000-000000000011', 'ORD-10011', '10000000-0000-4000-8000-000000000006', 'Grace Obi', 500.00, 'USD', 'COMPLETED', 'Furniture purchase', false, '2026-09-10T14:25:00Z', false),
('20000000-0000-4000-8000-000000000012', 'ORD-10012', '10000000-0000-4000-8000-000000000006', 'Grace Obi', 60.00, 'USD', 'COMPLETED', 'Mobile wallet top-up', false, '2026-09-11T07:45:00Z', true),
('20000000-0000-4000-8000-000000000013', 'ORD-10013', '10000000-0000-4000-8000-000000000001', 'Amara Okafor', 150.00, 'USD', 'COMPLETED', 'Hotel reservation', false, '2026-09-12T20:10:00Z', false),
('20000000-0000-4000-8000-000000000014', 'ORD-10014', '10000000-0000-4000-8000-000000000002', 'Daniel Adeyemi', 275.40, 'USD', 'COMPLETED', 'Restaurant payment - final sale', true, '2026-09-13T21:05:00Z', false),
('20000000-0000-4000-8000-000000000015', 'ORD-10015', '10000000-0000-4000-8000-000000000003', 'Fatima Bello', 95.00, 'USD', 'COMPLETED', 'Online clothing order', false, '2026-08-15T17:35:00Z', false);

-- ============================================================
-- REFUNDS
-- Covers every RefundStatus enum value.
-- The records deliberately represent different workflow stages.
-- ============================================================
INSERT INTO "Refund"
("id", "orderId", "accountName", "userId", "transactionId", "requestId", "amount", "reason", "status", "decision", "createdAt", "updatedAt") VALUES
('30000000-0000-4000-8000-000000000001', 'ORD-10001', 'Amara Okafor', '10000000-0000-4000-8000-000000000001', '20000000-0000-4000-8000-000000000001', 'req-demo-0001', 125.50, 'Merchant did not deliver the order', 'PENDING', NULL, '2026-09-15T08:00:00Z', '2026-09-15T08:00:00Z'),
('30000000-0000-4000-8000-000000000002', 'ORD-10002', 'Amara Okafor', '10000000-0000-4000-8000-000000000001', '20000000-0000-4000-8000-000000000002', 'req-demo-0002', 75.00, 'I was charged twice for the same subscription', 'COMPLETED', 'Approved: duplicate completed transaction and full amount matched.', '2026-09-05T09:00:00Z', '2026-09-06T11:00:00Z'),
('30000000-0000-4000-8000-000000000003', 'ORD-10006', 'Daniel Adeyemi', '10000000-0000-4000-8000-000000000002', '20000000-0000-4000-8000-000000000006', 'req-demo-0003', 850.00, 'Item arrived damaged', 'PROCESSING', 'Eligible refund request; processing payment reversal.', '2026-09-15T10:15:00Z', '2026-09-15T10:20:00Z'),
('30000000-0000-4000-8000-000000000004', 'ORD-10007', 'Fatima Bello', '10000000-0000-4000-8000-000000000003', '20000000-0000-4000-8000-000000000007', 'req-demo-0004', 35.75, 'Incorrect item received', 'APPROVED', 'Approved: completed transaction and requested amount matches transaction.', '2026-09-15T11:00:00Z', '2026-09-15T11:05:00Z'),
('30000000-0000-4000-8000-000000000005', 'ORD-10003', 'Amara Okafor', '10000000-0000-4000-8000-000000000001', '20000000-0000-4000-8000-000000000003', 'req-demo-0005', 310.00, 'I want to cancel this pending payment', 'REJECTED', 'Rejected: transaction is still pending and has not completed settlement.', '2026-09-15T12:00:00Z', '2026-09-15T12:02:00Z'),
('30000000-0000-4000-8000-000000000006', 'ORD-10004', 'Daniel Adeyemi', '10000000-0000-4000-8000-000000000002', '20000000-0000-4000-8000-000000000004', 'req-demo-0006', 49.99, 'The payment failed but I want a refund', 'REQUIRES_REVIEW', 'Manual review required: transaction failed; no completed charge is available for a standard refund.', '2026-09-15T12:30:00Z', '2026-09-15T12:35:00Z'),
('30000000-0000-4000-8000-000000000007', 'ORD-10005', 'Daniel Adeyemi', '10000000-0000-4000-8000-000000000002', '20000000-0000-4000-8000-000000000005', 'req-demo-0007', 220.00, 'Payment was reversed', 'FAILED', 'Refund failed: transaction was already reversed by the payment system.', '2026-09-15T13:00:00Z', '2026-09-15T13:10:00Z'),
('30000000-0000-4000-8000-000000000008', 'ORD-10008', 'Fatima Bello', '10000000-0000-4000-8000-000000000003', '20000000-0000-4000-8000-000000000008', 'req-demo-0008', 500.00, 'Partial refund for service issue', 'REQUIRES_REVIEW', 'Manual review required: requested amount is lower than the full transaction amount.', '2026-09-15T14:00:00Z', '2026-09-15T14:05:00Z'),
('30000000-0000-4000-8000-000000000009', 'ORD-10012', 'Grace Obi', '10000000-0000-4000-8000-000000000006', '20000000-0000-4000-8000-000000000012', 'req-demo-0009', 60.00, 'Unauthorized wallet top-up', 'COMPLETED', 'Approved and completed: completed transaction passed refund policy.', '2026-09-12T09:00:00Z', '2026-09-13T15:30:00Z');

-- ============================================================
-- AUDIT LOGS
-- Covers customer requests, worker validation, policy decisions,
-- admin review and developer/system events. Includes JSON metadata.
-- ============================================================
INSERT INTO "AuditLog"
("id", "refundId", "actorType", "actorId", "action", "note", "metadata", "createdAt") VALUES
('40000000-0000-4000-8000-000000000001', '30000000-0000-4000-8000-000000000001', 'LLM', NULL, 'REFUND_INTENT_EXTRACTED', 'Gemini identified a refund request from the customer conversation.', '{"intent":"refund_request","transaction_id":"20000000-0000-4000-8000-000000000001","amount":125.50,"confidence":0.96}', '2026-09-15T08:00:01Z'),
('40000000-0000-4000-8000-000000000002', '30000000-0000-4000-8000-000000000001', 'WORKER', NULL, 'REFUND_TICKET_CREATED', 'Refund ticket created for asynchronous processing.', '{"request_id":"req-demo-0001","queue":"refund.requested"}', '2026-09-15T08:00:02Z'),
('40000000-0000-4000-8000-000000000003', '30000000-0000-4000-8000-000000000002', 'WORKER', NULL, 'POLICY_APPROVED', 'Transaction status and requested amount passed policy validation.', '{"transaction_status":"COMPLETED","transaction_amount":75.00,"requested_amount":75.00,"matched_amount":true}', '2026-09-05T09:01:00Z'),
('40000000-0000-4000-8000-000000000004', '30000000-0000-4000-8000-000000000002', 'ADMIN', '10000000-0000-4000-8000-000000000005', 'REFUND_COMPLETED', 'Admin confirmed completion of the refund workflow.', '{"previous_status":"APPROVED","new_status":"COMPLETED"}', '2026-09-06T11:00:00Z'),
('40000000-0000-4000-8000-000000000005', '30000000-0000-4000-8000-000000000003', 'WORKER', NULL, 'REFUND_PROCESSING', 'Refund passed policy and entered processing.', '{"transaction_status":"COMPLETED","amount":850.00}', '2026-09-15T10:20:00Z'),
('40000000-0000-4000-8000-000000000006', '30000000-0000-4000-8000-000000000004', 'WORKER', NULL, 'POLICY_APPROVED', 'Full requested amount matched the completed transaction.', '{"transaction_status":"COMPLETED","transaction_amount":35.75,"requested_amount":35.75}', '2026-09-15T11:05:00Z'),
('40000000-0000-4000-8000-000000000007', '30000000-0000-4000-8000-000000000005', 'WORKER', NULL, 'POLICY_REJECTED', 'Refund rejected because the transaction is still pending.', '{"transaction_status":"PENDING","policy":"completed_transactions_only"}', '2026-09-15T12:02:00Z'),
('40000000-0000-4000-8000-000000000008', '30000000-0000-4000-8000-000000000006', 'WORKER', NULL, 'MANUAL_REVIEW_REQUIRED', 'Failed transaction requires manual investigation.', '{"transaction_status":"FAILED","reason":"no_completed_charge"}', '2026-09-15T12:35:00Z'),
('40000000-0000-4000-8000-000000000009', '30000000-0000-4000-8000-000000000007', 'WORKER', NULL, 'REFUND_FAILED', 'Refund operation could not proceed because the transaction was already reversed.', '{"transaction_status":"REVERSED","refund_status":"FAILED"}', '2026-09-15T13:10:00Z'),
('40000000-0000-4000-8000-000000000010', '30000000-0000-4000-8000-000000000008', 'ADMIN', '10000000-0000-4000-8000-000000000005', 'REVIEW_OPENED', 'Admin review opened for a partial refund request.', '{"requested_amount":500.00,"transaction_amount":1200.00,"difference":700.00}', '2026-09-15T14:06:00Z'),
('40000000-0000-4000-8000-000000000011', '30000000-0000-4000-8000-000000000009', 'WORKER', NULL, 'REFUND_COMPLETED', 'Refund completed after policy approval.', '{"transaction_status":"COMPLETED","amount":60.00}', '2026-09-13T15:30:00Z'),
('40000000-0000-4000-8000-000000000012', NULL, 'SYSTEM', NULL, 'SEED_DATA_LOADED', 'Demo dataset loaded successfully.', '{"environment":"demo","transaction_count":15,"refund_count":9,"user_count":6}', '2026-09-15T16:00:00Z');

-- ============================================================
-- IDEMPOTENCY KEYS
-- Covers fresh, already-processed and soon-expiring requests.
-- ============================================================
INSERT INTO "IdempotencyKey"
("id", "key", "userId", "requestHash", "responseId", "expiresAt", "createdAt") VALUES
('50000000-0000-4000-8000-000000000001', 'idem-demo-amara-001', '10000000-0000-4000-8000-000000000001', '6b1c1c8f4fcb9b0c5c8a7f0c5c4b0c4e3b5d2f3d4a5c6b7d8e9f001122334455', '30000000-0000-4000-8000-000000000001', '2026-10-15T08:00:00Z', '2026-09-15T08:00:00Z'),
('50000000-0000-4000-8000-000000000002', 'idem-demo-daniel-001', '10000000-0000-4000-8000-000000000002', '7c2d2d9f5fdbac1d6d9b8f1d6d5c1d5f4c6e3a4e5b6d7c8e9f00112233445566', '30000000-0000-4000-8000-000000000003', '2026-10-15T10:15:00Z', '2026-09-15T10:15:00Z'),
('50000000-0000-4000-8000-000000000003', 'idem-demo-fatima-001', '10000000-0000-4000-8000-000000000003', '8d3e3eaf6edcbd2e7eac9f2e7e6d2e6f5d7f4b5f6c7e8d9f0011223344556677', NULL, '2026-09-30T23:59:59Z', '2026-09-15T14:00:00Z'),
('50000000-0000-4000-8000-000000000004', 'idem-demo-grace-001', '10000000-0000-4000-8000-000000000006', '9e4f4fba7fedce3f8fbd0a3f8f7e3f7a6e8b5c6b7d8f9e001122334455667788', '30000000-0000-4000-8000-000000000009', '2026-10-15T09:00:00Z', '2026-09-15T09:00:00Z');

COMMIT;

-- Quick verification queries:
-- SELECT "role", COUNT(*) FROM "User" GROUP BY "role" ORDER BY "role";
-- SELECT "status", COUNT(*) FROM "Transaction" GROUP BY "status" ORDER BY "status";
-- SELECT "status", COUNT(*) FROM "Refund" GROUP BY "status" ORDER BY "status";
-- SELECT "actorType", COUNT(*) FROM "AuditLog" GROUP BY "actorType" ORDER BY "actorType";
-- SELECT COUNT(*) AS users FROM "User";
-- SELECT COUNT(*) AS transactions FROM "Transaction";
-- SELECT COUNT(*) AS refunds FROM "Refund";
-- SELECT COUNT(*) AS audit_logs FROM "AuditLog";
-- SELECT COUNT(*) AS idempotency_keys FROM "IdempotencyKey";
