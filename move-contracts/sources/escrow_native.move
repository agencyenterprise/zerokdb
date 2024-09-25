module escrow_native::escrow_native {
    use std::error;
    use std::signer;
    use std::string;
    use aptos_framework::coin;
    use aptos_framework::aptos_coin::AptosCoin;
    use aptos_framework::event;
    use aptos_framework::account;
    use aptos_std::table::{Self, Table};

    /// Errors
    const ENOT_OWNER_OR_RELAYER: u64 = 0x60001; // 393217
    const EINSUFFICIENT_FUNDS: u64 = 0x60002; // 393218
    const EINSUFFICIENT_LOCKED_FUNDS: u64 = 0x60003; // 393219
    const EESCROW_NOT_INITIALIZED: u64 = 0x60004; // 393220
    const EALREADY_INITIALIZED: u64 = 0x60005; // 393221
    const ENOT_OWNER: u64 = 0x60006; // 393222

    /// Events
    struct Deposited has drop, store {
        payer: address,
        amount: u64,
    }

    struct Locked has drop, store {
        payer: address,
        amount: u64,
    }

    struct Unlocked has drop, store {
        payer: address,
        amount: u64,
    }

    struct Paid has drop, store {
        payer: address,
        amount: u64,
    }

    struct Refunded has drop, store {
        payer: address,
        amount: u64,
    }

    struct Withdrawn has drop, store {
        payer: address,
        amount: u64,
    }

    struct UserEscrow has key {
        deposits: coin::Coin<AptosCoin>,
        locked: coin::Coin<AptosCoin>,
        deposit_events: event::EventHandle<Deposited>,
        lock_events: event::EventHandle<Locked>,
        unlock_events: event::EventHandle<Unlocked>,
        paid_events: event::EventHandle<Paid>,
        refund_events: event::EventHandle<Refunded>,
    }

    struct EscrowConfig has key {
        platform_fee_percentage: u64,
        relayer: address,
        fees: coin::Coin<AptosCoin>,
        withdraw_events: event::EventHandle<Withdrawn>,
    }

    public entry fun initialize(account: &signer, platform_fee_percentage: u64, relayer: address) {
        let account_addr = signer::address_of(account);
        assert!(!exists<EscrowConfig>(account_addr), error::already_exists(EALREADY_INITIALIZED));

        let config = EscrowConfig {
            platform_fee_percentage,
            relayer,
            fees: coin::zero<AptosCoin>(),
            withdraw_events: account::new_event_handle<Withdrawn>(account),
        };
        move_to(account, config);
    }

    public entry fun initialize_user(account: &signer) {
        let account_addr = signer::address_of(account);
        assert!(!exists<UserEscrow>(account_addr), error::already_exists(EALREADY_INITIALIZED));

        let user_escrow = UserEscrow {
            deposits: coin::zero<AptosCoin>(),
            locked: coin::zero<AptosCoin>(),
            deposit_events: account::new_event_handle<Deposited>(account),
            lock_events: account::new_event_handle<Locked>(account),
            unlock_events: account::new_event_handle<Unlocked>(account),
            paid_events: account::new_event_handle<Paid>(account),
            refund_events: account::new_event_handle<Refunded>(account),
        };
        move_to(account, user_escrow);
    }

    #[view]
    public fun balance_of(payer: address): u64 acquires UserEscrow {
        if (!exists<UserEscrow>(payer)) {
            return 0
        };
        let user_escrow = borrow_global<UserEscrow>(payer);
        coin::value(&user_escrow.deposits)
    }

    #[view]
    public fun locked_of(payer: address): u64 acquires UserEscrow {
        if (!exists<UserEscrow>(payer)) {
            return 0
        };
        let user_escrow = borrow_global<UserEscrow>(payer);
        coin::value(&user_escrow.locked)
    }

    public entry fun deposit(account: &signer, amount: u64) acquires UserEscrow {
        let account_addr = signer::address_of(account);

        // Ensure the user escrow is initialized
        if (!exists<UserEscrow>(account_addr)) {
            initialize_user(account);
        };

        assert!(coin::balance<AptosCoin>(account_addr) >= amount, error::invalid_argument(EINSUFFICIENT_FUNDS));

        // Ensure the account is registered for AptosCoin
        if (!coin::is_account_registered<AptosCoin>(account_addr)) {
            coin::register<AptosCoin>(account);
        };

        let deposit_coins = coin::withdraw<AptosCoin>(account, amount);

        let user_escrow = borrow_global_mut<UserEscrow>(account_addr);
        coin::merge(&mut user_escrow.deposits, deposit_coins);

        event::emit_event(&mut user_escrow.deposit_events, Deposited { payer: account_addr, amount });
    }

    #[view]
    public fun fees(): u64 acquires EscrowConfig {
        let escrow = borrow_global<EscrowConfig>(@escrow_native);
        coin::value(&escrow.fees)
    }

    public entry fun set_platform_fee_percentage(account: &signer, new_fee_percentage: u64) acquires EscrowConfig {
        let escrow = borrow_global_mut<EscrowConfig>(@escrow_native);
        assert!(signer::address_of(account) == @escrow_native, error::permission_denied(ENOT_OWNER));
        escrow.platform_fee_percentage = new_fee_percentage;
    }

    public entry fun lock(account: &signer, payer: address, amount: u64) acquires EscrowConfig, UserEscrow {
        let escrow = borrow_global<EscrowConfig>(@escrow_native);
        assert!(signer::address_of(account) == @escrow_native || signer::address_of(account) == escrow.relayer, ENOT_OWNER_OR_RELAYER);
        assert!(exists<UserEscrow>(payer), EINSUFFICIENT_FUNDS);

        let user_escrow = borrow_global_mut<UserEscrow>(payer);
        assert!(coin::value(&user_escrow.deposits) >= amount, EINSUFFICIENT_FUNDS);

        let lock_coins = coin::extract(&mut user_escrow.deposits, amount);
        coin::merge(&mut user_escrow.locked, lock_coins);
        event::emit_event(&mut user_escrow.lock_events, Locked { payer, amount });
    }

    public entry fun unlock(account: &signer, payer: address, amount: u64) acquires EscrowConfig, UserEscrow {
        let escrow = borrow_global<EscrowConfig>(@escrow_native);
        assert!(signer::address_of(account) == @escrow_native || signer::address_of(account) == escrow.relayer, error::permission_denied(ENOT_OWNER_OR_RELAYER));
        assert!(exists<UserEscrow>(payer), error::invalid_argument(EINSUFFICIENT_LOCKED_FUNDS));

        let user_escrow = borrow_global_mut<UserEscrow>(payer);
        assert!(coin::value(&user_escrow.locked) >= amount, error::invalid_argument(EINSUFFICIENT_LOCKED_FUNDS));

        let unlock_coins = coin::extract(&mut user_escrow.locked, amount);
        coin::merge(&mut user_escrow.deposits, unlock_coins);
        event::emit_event(&mut user_escrow.unlock_events, Unlocked { payer, amount });
    }

    public entry fun pay(account: &signer, payer: address, payee: address, amount: u64) acquires EscrowConfig, UserEscrow {
        let escrow = borrow_global_mut<EscrowConfig>(@escrow_native);
        assert!(signer::address_of(account) == @escrow_native || signer::address_of(account) == escrow.relayer, error::permission_denied(ENOT_OWNER_OR_RELAYER));
        assert!(exists<UserEscrow>(payer), error::invalid_argument(EINSUFFICIENT_LOCKED_FUNDS));

        let user_escrow = borrow_global_mut<UserEscrow>(payer);
        assert!(coin::value(&user_escrow.locked) >= amount, error::invalid_argument(EINSUFFICIENT_LOCKED_FUNDS));

        let pay_coins = coin::extract(&mut user_escrow.locked, amount);
        let fee_amount = (amount * escrow.platform_fee_percentage) / (100 * 1000000);
        let fee_coins = coin::extract(&mut pay_coins, fee_amount);
        coin::merge(&mut escrow.fees, fee_coins);

        coin::deposit(payee, pay_coins);
        event::emit_event(&mut user_escrow.paid_events, Paid { payer, amount });
    }

    public entry fun refund(account: &signer, amount: u64) acquires UserEscrow {
        let payer = signer::address_of(account);
        assert!(exists<UserEscrow>(payer), error::invalid_argument(EINSUFFICIENT_FUNDS));

        let user_escrow = borrow_global_mut<UserEscrow>(payer);
        let available_balance = coin::value(&user_escrow.deposits);
        assert!(available_balance >= amount, error::invalid_argument(EINSUFFICIENT_FUNDS));

        let refund_coins = coin::extract(&mut user_escrow.deposits, amount);
        coin::deposit(payer, refund_coins);
        event::emit_event(&mut user_escrow.refund_events, Refunded { payer, amount });
    }

    public entry fun withdraw(account: &signer, amount: u64) acquires EscrowConfig {
        let escrow = borrow_global_mut<EscrowConfig>(@escrow_native);
        assert!(
            signer::address_of(account) == @escrow_native || signer::address_of(account) == escrow.relayer,
            error::permission_denied(ENOT_OWNER_OR_RELAYER)
        );
        assert!(coin::value(&escrow.fees) >= amount, error::invalid_argument(EINSUFFICIENT_FUNDS));

        let withdraw_coins = coin::extract(&mut escrow.fees, amount);
        coin::deposit(signer::address_of(account), withdraw_coins);
        event::emit_event(&mut escrow.withdraw_events, Withdrawn { payer: signer::address_of(account), amount });
    }

    #[view]
    public fun get_user_info(payer: address): (u64, u64) acquires UserEscrow {
        if (!exists<UserEscrow>(payer)) {
            return (0, 0)
        };
        let user_escrow = borrow_global<UserEscrow>(payer);
        (coin::value(&user_escrow.deposits), coin::value(&user_escrow.locked))
    }

    #[test_only]
    use aptos_framework::coin::BurnCapability;
    #[test_only]
    use aptos_framework::timestamp;

    #[test_only]
    fun setup(aptos_framework: &signer, user: &signer): BurnCapability<AptosCoin> {
        timestamp::set_time_has_started_for_testing(aptos_framework);

        let (burn_cap, freeze_cap, mint_cap) = coin::initialize<AptosCoin>(
            aptos_framework,
            string::utf8(b"AptosCoin"),
            string::utf8(b"APT"),
            6,
            false,
        );
        account::create_account_for_test(signer::address_of(user));
        coin::register<AptosCoin>(user);
        let coins = coin::mint<AptosCoin>(1000000, &mint_cap);
        coin::deposit(signer::address_of(user), coins);
        coin::destroy_mint_cap(mint_cap);
        coin::destroy_freeze_cap(freeze_cap);

        burn_cap
    }

    #[test(aptos_framework = @0x1, admin = @escrow_native, user = @0x123, relayer = @0x456)]
    public fun test_initialize_and_deposit(
        aptos_framework: &signer, admin: &signer, user: &signer, relayer: &signer
    ) acquires UserEscrow {
        let burn_cap = setup(aptos_framework, user);
        account::create_account_for_test(signer::address_of(admin));
        account::create_account_for_test(signer::address_of(relayer));

        initialize(admin, 1000000, signer::address_of(relayer)); // 1% fee

        // Deposit funds
        deposit(user, 500000);

        // Check balance
        assert!(balance_of(signer::address_of(user)) == 500000, 0);

        coin::destroy_burn_cap(burn_cap);
    }

    #[test(aptos_framework = @0x1, admin = @escrow_native, user = @0x123, relayer = @0x456)]
    public fun test_lock_and_unlock(
        aptos_framework: &signer, admin: &signer, user: &signer, relayer: &signer
    ) acquires EscrowConfig, UserEscrow {
        test_initialize_and_deposit(aptos_framework, admin, user, relayer);

        // Lock funds
        lock(relayer, signer::address_of(user), 200000);
        assert!(locked_of(signer::address_of(user)) == 200000, 0);

        // Unlock funds
        unlock(relayer, signer::address_of(user), 100000);
        assert!(locked_of(signer::address_of(user)) == 100000, 0);
        assert!(balance_of(signer::address_of(user)) == 400000, 0);
    }

    #[test(aptos_framework = @0x1, admin = @escrow_native, user = @0x123, relayer = @0x456, payee = @0x789)]
    public fun test_pay(
        aptos_framework: &signer, admin: &signer, user: &signer, relayer: &signer, payee: &signer
    ) acquires EscrowConfig, UserEscrow {
        test_initialize_and_deposit(aptos_framework, admin, user, relayer);
        account::create_account_for_test(signer::address_of(payee));

        // Initialize coin store for payee
        coin::register<AptosCoin>(payee);

        // Lock funds
        lock(relayer, signer::address_of(user), 200000);

        // Pay
        pay(relayer, signer::address_of(user), signer::address_of(payee), 100000);

        // Check balances
        assert!(locked_of(signer::address_of(user)) == 100000, 0);
        assert!(balance_of(signer::address_of(user)) == 300000, 0);
        assert!(coin::balance<AptosCoin>(signer::address_of(payee)) == 99000, 0); // 1% fee deducted
        assert!(fees() == 1000, 0);
    }

    #[test(aptos_framework = @0x1, admin = @escrow_native, user = @0x123, relayer = @0x456)]
    public fun test_refund(
        aptos_framework: &signer, admin: &signer, user: &signer, relayer: &signer
    ) acquires UserEscrow {
        test_initialize_and_deposit(aptos_framework, admin, user, relayer);

        // Refund
        refund(user, 100000);

        // Check balance
        assert!(balance_of(signer::address_of(user)) == 400000, 0);
        assert!(coin::balance<AptosCoin>(signer::address_of(user)) == 600000, 0);
    }

    #[test(aptos_framework = @0x1, admin = @escrow_native, user = @0x123, relayer = @0x456)]
    #[expected_failure(abort_code = 393217)] // This is the error code for ENOT_OWNER_OR_RELAYER
    public fun test_unauthorized_withdraw(
        aptos_framework: &signer, admin: &signer, user: &signer, relayer: &signer
    ) acquires EscrowConfig, UserEscrow {
        test_initialize_and_deposit(aptos_framework, admin, user, relayer);

        // Try to withdraw as non-admin (should fail)
        withdraw(user, 1000);
    }
}
