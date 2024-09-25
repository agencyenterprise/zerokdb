module table_sequences::table_sequences {
    use std::signer;
    use aptos_framework::event;
    use aptos_framework::account;
    use aptos_framework::error;
    use std::string::{Self, String};
    use aptos_std::table::{Self, Table};

    const ESEQUENCE_NOT_EXIST: u64 = 1;
    const ESEQUENCE_ALREADY_EXISTS: u64 = 2;
    const EALREADY_INITIALIZED: u64 = 3;
    const ENOT_AUTHORIZED: u64 = 4;

    struct Sequence has store {
        id: u64,
        table_name: String,
        cid: String,
    }

    struct Sequences has key {
        sequences: Table<u64, Sequence>,
        next_id: u64,
    }

    struct OwnerCap has key {}

    #[event]
    struct SequenceCreatedEvent has drop, store {
        id: u64,
        table_name: String,
        cid: String,
    }

    #[event]
    struct SequenceUpdatedEvent has drop, store {
        id: u64,
        new_cid: String,
    }

    public entry fun initialize(account: &signer) {
        let account_addr = signer::address_of(account);
        assert!(!exists<Sequences>(account_addr), error::already_exists(EALREADY_INITIALIZED));

        let sequences = Sequences {
            sequences: table::new(),
            next_id: 1,
        };
        move_to(account, sequences);
        move_to(account, OwnerCap {});
    }

    public entry fun create_sequence(account: &signer, table_name: String, cid: String) acquires Sequences {
        let account_addr = signer::address_of(account);
        assert!(exists<OwnerCap>(account_addr), error::permission_denied(ENOT_AUTHORIZED));
        assert!(exists<Sequences>(account_addr), error::not_found(EALREADY_INITIALIZED));

        let sequences = borrow_global_mut<Sequences>(account_addr);
        let id = sequences.next_id;
        table::add(&mut sequences.sequences, id, Sequence { id, table_name, cid });
        sequences.next_id = id + 1;

        event::emit(SequenceCreatedEvent {
            id,
            table_name,
            cid,
        });
    }

    public entry fun update_sequence_cid(account: &signer, id: u64, new_cid: String) acquires Sequences {
        let account_addr = signer::address_of(account);
        assert!(exists<OwnerCap>(account_addr), ENOT_AUTHORIZED);
        assert!(exists<Sequences>(account_addr), error::not_found(EALREADY_INITIALIZED));

        let sequences = borrow_global_mut<Sequences>(account_addr);
        assert!(table::contains(&sequences.sequences, id), ESEQUENCE_NOT_EXIST);
        let sequence = table::borrow_mut(&mut sequences.sequences, id);
        sequence.cid = new_cid;

        event::emit(SequenceUpdatedEvent {
            id,
            new_cid,
        });
    }

    #[view]
    public fun get_sequence_by_id(addr: address, id: u64): (u64, String, String) acquires Sequences {
        assert!(exists<Sequences>(addr), error::not_found(EALREADY_INITIALIZED));
        let sequences = borrow_global<Sequences>(addr);
        assert!(table::contains(&sequences.sequences, id), ESEQUENCE_NOT_EXIST);
        let sequence = table::borrow(&sequences.sequences, id);
        (sequence.id, sequence.table_name, sequence.cid)
    }

    #[test(admin = @0x123)]
    public entry fun test_initialize(admin: &signer) acquires Sequences {
        let admin_addr = signer::address_of(admin);
        account::create_account_for_test(admin_addr);

        initialize(admin);

        let sequences = borrow_global<Sequences>(admin_addr);
        assert!(sequences.next_id == 1, 0);
        assert!(!table::contains(&sequences.sequences, 0), 1);
        assert!(exists<OwnerCap>(admin_addr), 2);
    }

    #[test(admin = @0x123)]
    public entry fun test_create_sequence(admin: &signer) acquires Sequences {
        let admin_addr = signer::address_of(admin);
        account::create_account_for_test(admin_addr);

        initialize(admin);

        create_sequence(admin, string::utf8(b"TestTable"), string::utf8(b"CID123"));

        let sequences = borrow_global<Sequences>(admin_addr);
        assert!(sequences.next_id == 2, 0);
        assert!(table::contains(&sequences.sequences, 1), 1);

        let sequence = table::borrow(&sequences.sequences, 1);
        assert!(sequence.id == 1, 2);
        assert!(sequence.table_name == string::utf8(b"TestTable"), 3);
        assert!(sequence.cid == string::utf8(b"CID123"), 4);
    }

    #[test(admin = @0x123)]
    public entry fun test_get_sequence_by_id(admin: &signer) acquires Sequences {
        let admin_addr = signer::address_of(admin);
        account::create_account_for_test(admin_addr);

        initialize(admin);
        create_sequence(admin, string::utf8(b"TestTable"), string::utf8(b"CID123"));

        let (id, table_name, cid) = get_sequence_by_id(admin_addr, 1);
        assert!(id == 1, 0);
        assert!(table_name == string::utf8(b"TestTable"), 1);
        assert!(cid == string::utf8(b"CID123"), 2);
    }

    #[test(admin = @0x123)]
    #[expected_failure(abort_code = ESEQUENCE_NOT_EXIST)]
    public entry fun test_get_non_existent_sequence(admin: &signer) acquires Sequences {
        let admin_addr = signer::address_of(admin);
        account::create_account_for_test(admin_addr);

        initialize(admin);

        get_sequence_by_id(admin_addr, 999);
    }

    #[test(admin = @0x123)]
    public entry fun test_update_sequence_cid(admin: &signer) acquires Sequences {
        let admin_addr = signer::address_of(admin);
        account::create_account_for_test(admin_addr);

        initialize(admin);
        create_sequence(admin, string::utf8(b"TestTable"), string::utf8(b"CID123"));

        update_sequence_cid(admin, 1, string::utf8(b"CID456"));

        let (_, _, new_cid) = get_sequence_by_id(admin_addr, 1);
        assert!(new_cid == string::utf8(b"CID456"), 0);
    }

    #[test(admin = @0x123)]
    #[expected_failure(abort_code = ESEQUENCE_NOT_EXIST)]
    public entry fun test_update_non_existent_sequence(admin: &signer) acquires Sequences {
        let admin_addr = signer::address_of(admin);
        account::create_account_for_test(admin_addr);

        initialize(admin);

        update_sequence_cid(admin, 999, string::utf8(b"CID456"));
    }

    #[test(admin = @0x123, other = @0x456)]
    #[expected_failure(abort_code = ENOT_AUTHORIZED)]
    public entry fun test_update_sequence_by_non_owner(admin: &signer, other: &signer) acquires Sequences {
        let admin_addr = signer::address_of(admin);
        let other_addr = signer::address_of(other);
        account::create_account_for_test(admin_addr);
        account::create_account_for_test(other_addr);

        initialize(admin);

        create_sequence(admin, string::utf8(b"TestTable"), string::utf8(b"CID123"));

        update_sequence_cid(other, 1, string::utf8(b"CID456"));
    }
}