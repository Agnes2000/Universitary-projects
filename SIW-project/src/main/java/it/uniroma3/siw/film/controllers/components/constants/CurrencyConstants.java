package it.uniroma3.siw.film.controllers.components.constants;

import java.util.Currency;
import java.util.Locale;

public final class CurrencyConstants {

    public static final String SIMBOLO_MONETA = Currency.getInstance(Locale.getDefault()).getSymbol();

    private CurrencyConstants() {}
    
}
