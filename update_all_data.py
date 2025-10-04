import crypto_collector
import market_cap.market_cap_report as market_cap_report

if __name__ == "__main__":
    # update all crypto currencies
    crypto_collector.main()
    market_cap_report.main()
